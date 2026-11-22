from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
import unittest
from pathlib import Path

from launcher_case import LAUNCH, STUBS, LauncherTestCase, conversation

STALE_RECORD = "99999 Mon Jan  1 00:00:00 2001"


class RobustnessTests(LauncherTestCase):
    def test_a_non_ascii_repository_path_works_without_a_utf8_locale(self) -> None:
        self.root = self.tmp / "café" / "repo"
        self.root.parent.mkdir()
        self.git("clone", "-q", str(self.origin), str(self.root))
        self.env["STUB_ROOT"] = str(self.root)
        c_locale = self.c_locale()

        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec", env=c_locale), name="f-spec")
        window = self.window_of(spec)
        orchestrator = ("--feature", "f", "--role", "orchestrator", "--window", window)
        orchestrator_pane, _ = self.started(self.launch(*orchestrator, env=c_locale), name="f-orchestrator")
        self.tmux("kill-pane", "-t", orchestrator_pane)
        resurrected = self.make_pane(self.worktree("f"), command="claude --continue")

        result = self.launch(*orchestrator, env=c_locale)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={resurrected}\n"), result.stderr)

    def test_the_first_spec_writer_never_takes_the_sidebar_of_its_new_window(self) -> None:
        program = self.sidebar_program()
        self.replace_stub(
            "workmux",
            body=f"""#!/bin/sh
before=$(tmux list-windows -a -F '#{{window_id}}')
{STUBS / "workmux"} "$@" || exit $?
[ "$1" = add ] || exit 0
for window in $(tmux list-windows -a -F '#{{window_id}}'); do
  case "$before" in *"$window"*) continue ;; esac
  sidebar=$(tmux split-window -d -h -b -f -l 20 -P -F '#{{pane_id}}' -t "$window" "exec {program} 86400")
  until [ "$(tmux display-message -p -t "$sidebar" '#{{pane_current_command}}')" = workmux ]; do sleep 0.05; done
done
""",
        )

        pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        self.assertIn("--name f-spec ", self.wait_for_claude(pane))
        commands = self.tmux("list-panes", "-t", self.window_of(pane), "-F", "#{pane_current_command}").split()
        self.assertIn("workmux", commands)

    def test_concurrent_launches_wait_for_a_slow_workmux_add(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        self.replace_stub("workmux", body=f'#!/bin/sh\n[ "$1" = add ] && sleep 12\nexec {STUBS / "workmux"} "$@"\n')
        phases = ("a", "b")
        launches = [
            subprocess.Popen([str(LAUNCH), "--feature", "f", "--role", "phase", "--phase", phase, "--window", self.window], env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for phase in phases
        ]
        results = []
        for launch in launches:
            stdout, stderr = launch.communicate(timeout=90)
            results.append(subprocess.CompletedProcess(launch.args, launch.returncode, stdout, stderr))

        for result, phase in zip(results, phases, strict=True):
            self.started(result, name=f"f-phase-{phase}")

    def test_a_claude_that_never_appears_fails_and_records_no_conversation(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        failing = self.tmp / "claude-fails"
        failing.touch()
        self.replace_stub("claude", body=f'#!/bin/sh\n[ -e {failing} ] && exit 1\nexec {STUBS / "claude"} "$@"\n')
        args = ("--feature", "f", "--role", "planner", "--window", self.window)

        result = self.launch(*args)

        self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
        self.assertRegex(result.stderr, r"claude did not start in %\d+")
        failing.unlink()
        pane, _ = self.started(self.launch(*args), name="f-planner")
        restarted = self.wait_for_claude(pane)
        self.assertIsNotNone(conversation(args=restarted, flag="--session-id"), restarted)
        self.assertIsNone(conversation(args=restarted, flag="--resume"), restarted)

    def test_outside_a_git_repository_fails_and_creates_nothing(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        elsewhere = self.tmp / "elsewhere"
        elsewhere.mkdir()
        panes = self.pane_ids()

        result = self.launch("--feature", "f", "--role", "planner", "--window", self.window, cwd=elsewhere)

        self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
        self.assertIn("cannot resolve the git common directory", result.stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertFalse(self.worktree("f-planner").exists())
        self.assertEqual(self.pane_ids(), panes)


class StaleLockTests(LauncherTestCase):
    def lock_held_by(self, process: subprocess.Popen, /, *, start: str | None = None) -> Path:
        return self.write_lock("f-planner", record=f"{process.pid} {start or self.start_time(process.pid)}")

    def planner_args(self) -> tuple[str, ...]:
        self.make_feature_worktree()
        self.make_orchestrator()
        return ("--feature", "f", "--role", "planner", "--window", self.window)

    def test_a_lock_left_by_a_killed_launch_is_taken_at_once(self) -> None:
        args = self.planner_args()
        holder = subprocess.Popen(["sleep", "60"])
        self.lock_held_by(holder)
        holder.send_signal(signal.SIGKILL)
        holder.wait()

        began = time.monotonic()
        self.started(self.launch(*args), name="f-planner")

        self.assertLess(time.monotonic() - began, 5)

    def test_a_lock_whose_holder_pid_now_belongs_to_another_process_is_taken_at_once(self) -> None:
        args = self.planner_args()
        other = subprocess.Popen(["sleep", "60"])
        self.addCleanup(other.kill)
        self.lock_held_by(other, start="Thu Jan  1 00:00:00 1970")

        began = time.monotonic()
        self.started(self.launch(*args), name="f-planner")

        self.assertLess(time.monotonic() - began, 5)

    def test_a_live_holder_makes_the_launch_wait_until_it_ends(self) -> None:
        args = self.planner_args()
        holder = subprocess.Popen(["sleep", "60"])
        self.addCleanup(holder.kill)
        self.lock_held_by(holder)

        launch = subprocess.Popen([str(LAUNCH), *args], env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(2)
        self.assertIsNone(launch.poll(), "the launch went ahead while the holder was alive")
        holder.kill()
        holder.wait()
        out, err = launch.communicate(timeout=20)

        self.assertEqual(launch.returncode, 0, err)
        self.assertTrue(out.startswith("started f-planner "), out)

    def launch_all(self, sessions: list[tuple[str, ...]], /) -> list[subprocess.CompletedProcess]:
        launches = [
            subprocess.Popen([str(LAUNCH), "--feature", "f", *args, "--window", self.window], env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for args in sessions
        ]
        results = []
        for launch in launches:
            stdout, stderr = launch.communicate(timeout=120)
            results.append(subprocess.CompletedProcess(launch.args, launch.returncode, stdout, stderr))
        return results

    def test_concurrent_launches_past_a_stale_session_lock_start_one_copy(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        for phase in ("a", "b", "c", "d"):
            name = f"f-phase-{phase}"
            self.make_worktree(name=name, base="f")
            self.write_lock(name, record=STALE_RECORD)

            results = self.launch_all([("--role", "phase", "--phase", phase)] * 8)

            self.assertEqual([result.returncode for result in results], [0] * 8, [result.stderr for result in results])
            self.assertEqual(sorted(result.stdout.split()[0] for result in results), ["alive"] * 7 + ["started"], name)
            self.assertEqual(len(self.named_claudes(name)), 1, name)

    def test_concurrent_launches_past_a_stale_window_lock_share_one_full_height_column(self) -> None:
        self.make_feature_worktree()
        orchestrator = self.make_orchestrator()
        phases = [f"p{index}" for index in range(6)]
        for phase in phases:
            self.make_worktree(name=f"f-phase-{phase}", base="f")
        self.write_lock(f"window-{self.window.lstrip('@')}", record=STALE_RECORD)

        results = self.launch_all([("--role", "phase", "--phase", phase) for phase in phases])

        new = [self.started(result, name=f"f-phase-{phase}").pane for result, phase in zip(results, phases, strict=True)]
        after = self.geometry()
        self.assertEqual(len({(after[pane].left, after[pane].width) for pane in new}), 1, after)
        self.assertGreater(after[new[0]].left, after[orchestrator].left + after[orchestrator].width)
        height = int(self.tmux("display-message", "-p", "-t", self.window, "#{window_height}"))
        self.assertEqual(min(after[pane].top for pane in new), 0, after)
        self.assertEqual(max(after[pane].top + after[pane].height for pane in new), height, after)


class StartTimeTests(LauncherTestCase):
    """Two launches in different time zones or locales must read each other's lock alike."""

    def environment(self, **settings: str) -> dict[str, str]:
        kept = {key: value for key, value in self.env.items() if key not in {"LANG", "TZ"} and not key.startswith("LC_")}
        return {**kept, **settings}

    def skip_unless_ps_differs(self, *, first: dict[str, str], second: dict[str, str], reason: str) -> None:
        def lstart(env: dict[str, str]) -> str:
            return subprocess.run(["ps", "-o", "lstart=", "-p", str(os.getpid())], env=env, capture_output=True, text=True, check=True).stdout.strip()

        if lstart(first) == lstart(second):
            self.skipTest(reason)

    def assert_one_copy(self, *, first: dict[str, str], second: dict[str, str]) -> None:
        self.make_feature_worktree()
        self.make_worktree(name="f-planner", base="f")
        self.make_orchestrator()
        self.tmux("set-environment", "-g", "STUB_CLAUDE_DELAY", "3")
        command = [str(LAUNCH), "--feature", "f", "--role", "planner", "--window", self.window]
        holder = subprocess.Popen(command, env=first, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.wait_for(lambda: os.path.lexists(self.lock_path("f-planner")), message="the first launch took no lock")
        waiter = subprocess.Popen(command, env=second, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        outputs = [launch.communicate(timeout=60) for launch in (holder, waiter)]

        self.assertEqual([holder.returncode, waiter.returncode], [0, 0], outputs)
        self.assertTrue(outputs[0][0].startswith("started f-planner "), outputs)
        self.assertTrue(outputs[1][0].startswith("alive f-planner "), outputs)
        self.assertEqual(len(self.named_claudes("f-planner")), 1)

    def test_a_launch_in_another_time_zone_sees_the_live_holder(self) -> None:
        first, second = self.environment(LC_ALL="C", TZ="UTC"), self.environment(LC_ALL="C", TZ="Asia/Tokyo")
        self.skip_unless_ps_differs(first=first, second=second, reason="ps prints the same start time in UTC and Asia/Tokyo here, so the time zone data is missing")
        self.assert_one_copy(first=first, second=second)

    def test_a_launch_in_another_locale_sees_the_live_holder(self) -> None:
        first, second = self.environment(LC_ALL="en_GB.UTF-8"), self.environment(LC_ALL="C")
        self.skip_unless_ps_differs(first=first, second=second, reason="ps prints the same start time in en_GB.UTF-8 and C here: it ignores the locale, or en_GB.UTF-8 is not installed")
        self.assert_one_copy(first=first, second=second)


if __name__ == "__main__":
    unittest.main()


class IdlePaneTests(LauncherTestCase):
    """A session's left-over pane is reused only while it sits at an interactive shell."""

    def left_over_pane(self, *, command: list[str], ready: str) -> tuple[tuple[str, ...], str]:
        self.make_feature_worktree()
        self.make_orchestrator()
        (self.tmp / ".zshrc").write_text("")
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        pane, _ = self.started(self.launch(*args), name="f-phase-p")
        self.wait_for_claude(pane)
        self.kill_claude("f-phase-p")
        self.tmux("respawn-pane", "-k", "-t", pane, *command)
        foreground = lambda: any(row.args == ready for row in self.processes())
        self.wait_for(foreground, message=f"{ready!r} did not start in {pane}")
        return args, pane

    def assert_busy(self, *, command: list[str], ready: str) -> None:
        args, pane = self.left_over_pane(command=command, ready=ready)

        restarted, _ = self.started(self.launch(*args), name="f-phase-p")

        self.assertNotEqual(restarted, pane, f"{ready!r} counted as idle")
        self.assertTrue(any(row.args == ready for row in self.processes()), f"{ready!r} was killed")

    def assert_idle(self, *, command: list[str], ready: str) -> None:
        args, pane = self.left_over_pane(command=command, ready=ready)

        restarted, _ = self.started(self.launch(*args), name="f-phase-p")

        self.assertEqual(restarted, pane, f"{ready!r} counted as busy")

    def zsh(self) -> str:
        zsh = shutil.which("zsh")
        if zsh is None:
            self.skipTest("zsh is not installed")
        return zsh

    # Each shell blocks in the read builtin, so it is the only foreground process
    # and only its argument list can show that it is busy.
    def test_a_shell_running_a_script_is_busy(self) -> None:
        script = self.tmp / "build.sh"
        script.write_text("read -r line\n")
        self.assert_busy(command=["bash", str(script)], ready=f"bash {script}")

    def test_a_shell_running_a_command_is_busy(self) -> None:
        self.assert_busy(command=["sh", "-c", "read -r line; true"], ready="sh -c read -r line; true")

    def test_a_bare_interactive_bash_is_idle(self) -> None:
        self.assert_idle(command=["bash"], ready="bash")

    def test_a_login_zsh_is_idle(self) -> None:
        zsh = self.zsh()
        self.assert_idle(command=[zsh, "-l"], ready=f"{zsh} -l")

    def test_a_zsh_started_as_a_login_shell_by_name_is_idle(self) -> None:
        zsh = self.zsh()
        self.assert_idle(command=["bash", "-c", f"exec -a -zsh {zsh}"], ready="-zsh")


class NarrowColumnsTests(LauncherTestCase):
    def test_an_exported_columns_does_not_hide_a_live_session(self) -> None:
        # procps cuts ps output to $COLUMNS even into a pipe; macOS's ps does not.
        self.make_feature_worktree()
        narrow = dict(self.env, COLUMNS="40")
        args = ("--feature", "f", "--role", "phase", "--phase", "migrate-the-invoice-tables-to-the-new-schema", "--window", self.window)
        self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window, env=narrow)
        first, _ = self.started(self.launch(*args, env=narrow), name="f-phase-migrate-the-invoice-tables-to-the-new-schema")

        second = self.launch(*args, env=narrow)

        self.assertEqual((second.returncode, second.stdout), (0, f"alive f-phase-migrate-the-invoice-tables-to-the-new-schema pane={first}\n"), second.stderr)
        self.assertEqual(len(self.named_claudes("f-phase-migrate-the-invoice-tables-to-the-new-schema")), 1)


class DevelopersClaudeTests(LauncherTestCase):
    """A plain claude the developer opens in the feature worktree is never the orchestrator."""

    def crashed_orchestrator_beside_a_developers_claude(self) -> tuple[tuple[str, ...], str, str]:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = self.window_of(spec)
        orchestrator_args = ("--feature", "f", "--role", "orchestrator", "--window", window)
        orchestrator, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")
        self.wait_for_claude(orchestrator)
        developer = self.tmux("split-window", "-d", "-h", "-P", "-F", "#{pane_id}", "-t", spec, "-c", str(self.worktree("f")), "claude").strip()
        self.wait_for_claude(developer)
        self.kill_claude("f-orchestrator")
        return orchestrator_args, orchestrator, developer

    def test_a_crashed_orchestrator_restarts_in_its_own_pane_beside_a_developers_claude(self) -> None:
        orchestrator_args, orchestrator, developer = self.crashed_orchestrator_beside_a_developers_claude()

        restarted, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")

        self.assertEqual(restarted, orchestrator)
        self.assertIn("--resume", self.wait_for_claude(orchestrator))
        self.assertEqual((self.claude_in_pane(developer) or "").split(), ["claude"])

    def test_a_resurrected_orchestrator_beside_a_developers_claude_still_places_sessions(self) -> None:
        orchestrator_args, orchestrator, developer = self.crashed_orchestrator_beside_a_developers_claude()
        window = orchestrator_args[-1]
        self.tmux("kill-pane", "-t", orchestrator)
        resurrected = self.tmux("split-window", "-d", "-v", "-P", "-F", "#{pane_id}", "-t", developer, "-c", str(self.worktree("f")), "claude --continue").strip()
        self.wait_for_claude(resurrected)

        result = self.launch("--feature", "f", "--role", "planner", "--window", window)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.launch(*orchestrator_args).stdout, f"alive f-orchestrator pane={resurrected}\n")

    def plain_claude_in_place_of(self, name: str, /) -> str:
        """The developer types a plain claude in the session's own pane after its claude exits; returns the session's stored conversation id."""
        pane, stored = next((row.pane, conversation(args=row.args, flag="--session-id")) for row in self.named_claudes(name))
        self.kill_claude(name)
        self.tmux("respawn-pane", "-k", "-t", pane, "-c", str(self.worktree("f")), "claude")
        self.wait_for_claude(pane)
        return stored

    def test_a_plain_claude_in_the_orchestrators_own_pane_is_not_the_orchestrator(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = self.window_of(spec)
        orchestrator_args = ("--feature", "f", "--role", "orchestrator", "--window", window)
        old, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")
        self.wait_for_claude(old)
        stored = self.plain_claude_in_place_of("f-orchestrator")

        new, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")

        self.assertNotEqual(new, old)
        self.assertEqual(conversation(args=self.wait_for_claude(new), flag="--resume"), stored)
        self.assertEqual((self.claude_in_pane(old) or "").split(), ["claude"])
        self.started(self.launch("--feature", "f", "--role", "planner", "--window", window), name="f-planner")
        self.assertEqual(self.launch(*orchestrator_args).stdout, f"alive f-orchestrator pane={new}\n")

    def test_a_plain_claude_in_the_spec_writers_own_pane_is_not_the_spec_writer(self) -> None:
        old, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = self.window_of(old)
        self.wait_for_claude(old)
        stored = self.plain_claude_in_place_of("f-spec")

        documented = self.launch("--feature", "f", "--role", "spec")
        self.assertEqual((documented.returncode, documented.stdout), (2, ""), documented.stderr)
        self.assertIn("--window", documented.stderr)
        new, _ = self.started(self.launch("--feature", "f", "--role", "spec", "--window", window), name="f-spec")

        self.assertNotEqual(new, old)
        self.assertEqual(conversation(args=self.wait_for_claude(new), flag="--resume"), stored)
        self.assertEqual((self.claude_in_pane(old) or "").split(), ["claude"])
        self.assertEqual(self.launch("--feature", "f", "--role", "spec").stdout, f"alive f-spec pane={new}\n")


class SpecWriterRestartTests(LauncherTestCase):
    def test_the_documented_call_restarts_a_crashed_spec_writer_in_its_own_pane(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        self.wait_for_claude(spec)
        self.kill_claude("f-spec")

        restarted, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        self.assertEqual(restarted, spec)
        self.assertIn("--resume", self.wait_for_claude(spec))

    def test_the_documented_call_reports_a_live_spec_writer(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        self.wait_for_claude(spec)

        result = self.launch("--feature", "f", "--role", "spec")

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-spec pane={spec}\n"), result.stderr)

    def test_a_spec_writer_whose_pane_is_gone_needs_a_window(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        self.wait_for_claude(spec)
        self.tmux("kill-pane", "-t", spec)

        result = self.launch("--feature", "f", "--role", "spec")

        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("--window", result.stderr)

    def test_a_crashed_orchestrator_started_by_a_resurrected_spec_writer_restarts(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        self.wait_for_claude(spec)
        self.tmux("kill-window", "-t", self.window_of(spec))
        resurrected = self.make_pane(self.worktree("f"), command="claude --continue")
        orchestrator_args = ("--feature", "f", "--role", "orchestrator", "--window", self.window)
        orchestrator, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")
        self.wait_for_claude(orchestrator)
        self.kill_claude("f-orchestrator")

        restarted, _ = self.started(self.launch(*orchestrator_args), name="f-orchestrator")

        self.assertEqual(restarted, orchestrator)
        self.assertIn("--resume", self.wait_for_claude(orchestrator))
        self.assertEqual((self.claude_in_pane(resurrected) or "").split(), ["claude", "--continue"])

    def test_a_resurrected_spec_writer_is_alive(self) -> None:
        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        self.wait_for_claude(spec)
        self.tmux("kill-window", "-t", self.window_of(spec))
        resurrected = self.make_pane(self.worktree("f"), command="claude --continue")
        panes = len(self.panes())

        for args in (("--feature", "f", "--role", "spec"), ("--feature", "f", "--role", "spec", "--window", self.window)):
            with self.subTest(args=args):
                result = self.launch(*args)

                self.assertEqual((result.returncode, result.stdout), (0, f"alive f-spec pane={resurrected}\n"), result.stderr)
                self.assertEqual(len(self.panes()), panes)
                self.assertEqual(len(self.claude_processes()), 1)
