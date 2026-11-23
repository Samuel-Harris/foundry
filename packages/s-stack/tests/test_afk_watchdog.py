from __future__ import annotations

import hashlib
import os
import plistlib
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from launcher_case import LAUNCH, STUBS, LauncherTestCase

WATCHDOG = LAUNCH.parent / "afk-watchdog.sh"
STAMP = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"
ON_MACOS = sys.platform == "darwin"


class WatchdogCase(LauncherTestCase):
    def watchdog(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([str(WATCHDOG), *args], env=self.env, cwd=cwd or self.root, capture_output=True, text=True, timeout=120)

    def common_dir(self) -> str:
        return os.path.realpath(self.root / ".git")

    def write_marker(self, worktree: Path, content: str) -> Path:
        git_dir = Path(self.git("-C", str(worktree), "rev-parse", "--absolute-git-dir").strip())
        marker = git_dir / "s-stack-afk"
        marker.write_text(content)
        return marker


class ArgumentTests(unittest.TestCase):
    def test_bad_arguments_exit_2_with_the_usage(self) -> None:
        for args in ([], ["start"], ["run"], ["run", "a", "b"], ["status", "extra"]):
            with self.subTest(args=args):
                result = subprocess.run([str(WATCHDOG), *args], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Usage:", result.stderr)


class RunTests(WatchdogCase):
    def lines_by_subject(self, stdout: str, *subjects: str) -> list[str]:
        """git lists linked worktrees in no promised order, so each line is found by its second word."""
        by_subject = {line.split()[1]: line for line in stdout.splitlines()}
        self.assertEqual(sorted(by_subject), sorted(subjects), stdout)
        self.assertEqual(len(stdout.splitlines()), len(subjects), stdout)
        return [by_subject[subject] for subject in subjects]

    def test_no_marker_prints_nothing_and_starts_nothing(self) -> None:
        self.make_feature_worktree()

        result = self.watchdog("run", self.common_dir())

        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        self.assertEqual(self.claude_processes(), [])

    def test_a_failed_launch_does_not_stop_the_other_marker(self) -> None:
        self.write_marker(self.make_worktree(name="f", base="origin/main"), f"f {self.window}\n")
        self.write_marker(self.make_worktree(name="g", base="origin/main"), "g @999\n")

        result = self.watchdog("run", self.common_dir())

        self.assertEqual(result.returncode, 1, result.stderr)
        f, g = self.lines_by_subject(result.stdout, "f", "g")
        self.assertRegex(f, rf"^{STAMP} f started f-orchestrator pane=%\d+ worktree={re.escape(str(self.worktree('f')))}$")
        self.assertRegex(g, rf"^{STAMP} g failed [1-9]\d*$")
        self.assertIn("launch.sh:", result.stderr)
        self.assertEqual(len(self.named_claudes("f-orchestrator")), 1)

    def test_a_malformed_marker_is_reported_and_skipped(self) -> None:
        marker = self.write_marker(self.make_worktree(name="f", base="origin/main"), "f\n")
        self.write_marker(self.make_worktree(name="g", base="origin/main"), f"g {self.window}\n")

        result = self.watchdog("run", self.common_dir())

        self.assertEqual(result.returncode, 1, result.stderr)
        malformed, g = self.lines_by_subject(result.stdout, "malformed", "g")
        self.assertRegex(malformed, rf"^{STAMP} malformed marker={re.escape(str(marker))}$")
        self.assertRegex(g, rf"^{STAMP} g started g-orchestrator ")
        self.assertEqual(self.named_claudes("f-orchestrator"), [])


@unittest.skipUnless(ON_MACOS, "launchd exists only on macOS")
class LaunchdTests(WatchdogCase):
    def setUp(self) -> None:
        super().setUp()
        (self.bin / "launchctl").symlink_to(STUBS / "launchctl")
        self.launchctl_log = self.tmp / "launchctl.log"
        self.env["STUB_LAUNCHCTL_LOG"] = str(self.launchctl_log)
        self.assertEqual(shutil.which("launchctl", path=self.env["PATH"]), str(self.bin / "launchctl"))
        self.label = "com.s-stack.afk-watchdog." + hashlib.sha1(self.common_dir().encode()).hexdigest()[:8]
        self.plist = self.tmp / "Library/LaunchAgents" / f"{self.label}.plist"
        self.domain = f"gui/{os.getuid()}"

    def launchctl_calls(self) -> list[str]:
        return self.launchctl_log.read_text().splitlines() if self.launchctl_log.exists() else []

    def install(self) -> dict:
        result = self.watchdog("install")
        self.assertEqual((result.returncode, result.stdout), (0, f"installed {self.label} plist={self.plist}\n"), result.stderr)
        with self.plist.open("rb") as handle:
            return plistlib.load(handle)

    def test_install_writes_the_job_and_loads_it(self) -> None:
        self.env["LANG"] = "en_GB.UTF-8"

        job = self.install()

        log = str(self.tmp / "Library/Logs/s-stack-afk-watchdog.log")
        self.assertEqual(job["Label"], self.label)
        self.assertEqual(job["ProgramArguments"], ["/bin/bash", str(WATCHDOG), "run", self.common_dir()])
        self.assertEqual((job["StartInterval"], job["RunAtLoad"]), (1200, False))
        self.assertEqual((job["StandardOutPath"], job["StandardErrorPath"]), (log, log))
        self.assertEqual(job["EnvironmentVariables"], {key: self.env[key] for key in ("PATH", "HOME", "TMUX_TMPDIR", "LANG")})
        self.assertEqual(self.watchdog("status").stdout, f"installed {self.label}\n")

    def test_values_are_escaped_and_unset_variables_left_out(self) -> None:
        self.env.pop("LANG", None)
        self.env["TMUX_TMPDIR"] = str(self.tmp / "a&b <c> \"d\"")

        job = self.install()

        self.assertEqual(job["EnvironmentVariables"], {key: self.env[key] for key in ("PATH", "HOME", "TMUX_TMPDIR")})

    def test_reinstalling_replaces_the_job(self) -> None:
        self.install()
        self.env["LANG"] = "fr_FR.UTF-8"

        job = self.install()

        self.assertEqual(job["EnvironmentVariables"]["LANG"], "fr_FR.UTF-8")
        self.assertEqual([p.name for p in self.plist.parent.iterdir()], [self.plist.name])
        self.assertEqual(self.watchdog("status").stdout, f"installed {self.label}\n")

    def test_status_and_remove(self) -> None:
        self.assertEqual(self.watchdog("status").stdout, f"absent {self.label}\n")
        self.install()
        self.assertEqual(self.watchdog("status").stdout, f"installed {self.label}\n")

        removed = self.watchdog("remove")

        self.assertEqual((removed.returncode, removed.stdout), (0, f"removed {self.label}\n"), removed.stderr)
        self.assertFalse(self.plist.exists())
        self.assertEqual(self.watchdog("status").stdout, f"absent {self.label}\n")
        self.assertEqual(self.watchdog("remove").stdout, f"absent {self.label}\n")

    def test_status_is_absent_when_the_plist_is_not_loaded(self) -> None:
        self.install()
        self.watchdog("remove")
        self.plist.write_text("")

        self.assertEqual(self.watchdog("status").stdout, f"absent {self.label}\n")

    def test_install_outside_a_repository_fails(self) -> None:
        result = self.watchdog("install", cwd=self.tmp)

        self.assertEqual(result.returncode, 1)
        self.assertIn("git repository", result.stderr)
        self.assertEqual(self.launchctl_calls(), [])

    def test_the_job_restarts_the_orchestrator_with_only_its_own_environment(self) -> None:
        self.replace_stub(
            "workmux",
            body=f"#!/bin/sh\nSTUB_ROOT='{self.root}' STUB_WORKMUX_LOG='{self.workmux_log}' exec '{STUBS / 'workmux'}' \"$@\"\n",
        )
        feature = self.make_feature_worktree()
        job = self.install()

        def run_job() -> subprocess.CompletedProcess:
            assignments = [f"{key}={value}" for key, value in job["EnvironmentVariables"].items()]
            return subprocess.run(["env", "-i", *assignments, *job["ProgramArguments"]], cwd="/", capture_output=True, text=True, timeout=120)

        idle = run_job()
        self.assertEqual((idle.returncode, idle.stdout), (0, ""), idle.stderr)
        self.assertEqual(self.claude_processes(), [])

        self.write_marker(feature, f"f {self.window}\n")
        first = run_job()

        self.assertEqual(first.returncode, 0, first.stderr)
        match = re.fullmatch(rf"{STAMP} f started f-orchestrator pane=(%\d+) worktree=\S+\n", first.stdout)
        self.assertIsNotNone(match, first.stdout)
        pane = match.group(1)
        self.assertEqual(self.window_of(pane), self.window)
        self.assertIn("--name f-orchestrator ", self.wait_for_claude(pane))

        second = run_job()

        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertRegex(second.stdout, rf"^{STAMP} f alive f-orchestrator pane={pane}\n$")


@unittest.skipUnless(ON_MACOS, "keep-awake uses caffeinate, which exists only on macOS")
class KeepAwakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.bin / "caffeinate").symlink_to(STUBS / "caffeinate")
        self.caffeinate_log = self.tmp / "caffeinate.log"
        self.caffeinate_log.touch()
        self.env = {"PATH": f"{self.bin}:/usr/bin:/bin", "HOME": str(self.tmp), "STUB_CAFFEINATE_LOG": str(self.caffeinate_log)}
        self.assertEqual(shutil.which("caffeinate", path=self.env["PATH"]), str(self.bin / "caffeinate"))
        # A Bash whose process name is claude stands in for the Claude Code session; macOS kills an unsigned copy.
        self.claude_program = self.tmp / "session" / "claude"
        self.claude_program.parent.mkdir()
        shutil.copy("/bin/bash", self.claude_program)
        subprocess.run(["codesign", "-f", "-s", "-", str(self.claude_program)], check=True, capture_output=True)
        self.addCleanup(self.kill_caffeinates)

    def start_session(self) -> subprocess.Popen:
        session = subprocess.Popen([str(self.claude_program)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=self.env, cwd=self.tmp)
        self.addCleanup(session.stdout.close)
        self.addCleanup(session.stdin.close)
        self.addCleanup(session.wait, timeout=10)
        self.addCleanup(session.kill)
        return session

    def call(self, session: subprocess.Popen, subcommand: str) -> tuple[int, str]:
        """Runs the script as the session's Bash tool would, a child of the claude process."""
        session.stdin.write(f"'{WATCHDOG}' {subcommand} 2>&1; echo \"exit=$?\"\n".encode())
        session.stdin.flush()
        output = b""
        deadline = time.monotonic() + 30
        while b"exit=" not in output or not output.endswith(b"\n"):
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([session.stdout], [], [], remaining)[0]:
                self.fail(f"{subcommand} did not finish: {output!r}")
            output += os.read(session.stdout.fileno(), 4096)
        text, _, code = output.decode().rpartition("exit=")
        return int(code), text

    def caffeinates(self) -> dict[int, str]:
        out = subprocess.run(["ps", "-A", "-ww", "-o", "pid=,args="], capture_output=True, text=True, check=True).stdout
        rows = (line.split(None, 1) for line in out.splitlines())
        return {int(row[0]): " ".join(row[1].split()) for row in rows if len(row) == 2 and row[1].split()[0] == "caffeinate"}

    def caffeinates_waiting_on(self, pid: int) -> list[int]:
        return [p for p, args in self.caffeinates().items() if args == f"caffeinate -i -s -w {pid}"]

    def kill_caffeinates(self) -> None:
        for line in self.caffeinate_log.read_text().splitlines():
            for pid in self.caffeinates_waiting_on(int(line.split()[-1])):
                os.kill(pid, signal.SIGTERM)

    def wait_until(self, predicate, *, message: str) -> None:
        deadline = time.monotonic() + 10
        while not predicate():
            if time.monotonic() > deadline:
                self.fail(message)
            time.sleep(0.05)

    def test_keep_awake_starts_one_caffeinate_on_the_session_and_stop_ends_it(self) -> None:
        session = self.start_session()

        code, out = self.call(session, "keep-awake")

        self.assertEqual(code, 0, out)
        match = re.fullmatch(rf"awake claude={session.pid} caffeinate=(\d+)\n", out)
        self.assertIsNotNone(match, out)
        caffeinate = int(match.group(1))
        self.wait_until(lambda: self.caffeinates_waiting_on(session.pid) == [caffeinate], message="no caffeinate waits on the session")
        self.assertEqual(self.caffeinate_log.read_text(), f"-i -s -w {session.pid}\n")

        again = self.call(session, "keep-awake")

        self.assertEqual(again, (0, out))
        self.assertEqual(self.caffeinates_waiting_on(session.pid), [caffeinate])
        self.assertEqual(len(self.caffeinate_log.read_text().splitlines()), 1)

        stopped = self.call(session, "stop-keep-awake")

        self.assertEqual(stopped, (0, f"stopped caffeinate={caffeinate}\n"))
        self.wait_until(lambda: not self.caffeinates_waiting_on(session.pid), message="caffeinate still runs")
        self.assertEqual(self.call(session, "stop-keep-awake"), (0, "none\n"))

    def test_keep_awake_with_no_claude_above_it_fails(self) -> None:
        out = self.tmp / "out"
        # The subshell is orphaned before the script runs, so nothing above it is claude, not even the session running these tests.
        subprocess.run(["/bin/sh", "-c", '( sleep 1; "$0" keep-awake; echo "exit=$?" ) > "$1" 2>&1 &', str(WATCHDOG), str(out)], env=self.env, check=True, timeout=10)

        self.wait_until(lambda: "exit=" in out.read_text() if out.exists() else False, message="keep-awake did not finish")

        self.assertIn("no claude process above this script", out.read_text())
        self.assertTrue(out.read_text().endswith("exit=1\n"), out.read_text())
        self.assertEqual(self.caffeinate_log.read_text(), "")


if __name__ == "__main__":
    unittest.main()
