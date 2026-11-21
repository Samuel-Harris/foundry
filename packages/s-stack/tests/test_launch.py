from __future__ import annotations

import os
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import Callable, NamedTuple, TypeVar

LAUNCH = Path(__file__).resolve().parents[1] / ".apm/skills/sam-mode/scripts/launch.sh"
STUBS = Path(__file__).resolve().parent / "stubs"
ROADMAP_ID = "2026-11-20_21-37-12-f"
T = TypeVar("T")


class PsRow(NamedTuple):
    pid: int
    ppid: int
    args: str


class ClaudeProcess(NamedTuple):
    pid: int
    args: str
    pane: str


class Started(NamedTuple):
    pane: str
    worktree: str


PANE_FORMAT = "#{pane_id} #{pane_pid} #{pane_width} #{pane_height} #{window_id}"

def conversation(args: str, *, flag: str) -> str | None:
    words = args.split()
    return words[words.index(flag) + 1] if flag in words else None


def build_system_bin(target: Path) -> None:
    """Every system tool except the ones a test must be able to remove."""
    target.mkdir()
    withheld = {"tmux", "workmux", "claude", "gh"}
    for directory in ("/usr/bin", "/bin"):
        for entry in os.listdir(directory):
            link = target / entry
            if entry not in withheld and not link.exists():
                link.symlink_to(os.path.join(directory, entry))
    for tool in ("git", "python3", "perl"):
        found = shutil.which(tool)
        if found:
            link = target / tool
            if link.is_symlink():
                link.unlink()
            link.symlink_to(found)


@unittest.skipUnless(shutil.which("tmux"), "tmux is not on PATH, so the launcher cannot be exercised")
class LauncherTestCase(unittest.TestCase):
    system_bin: Path
    _class_tmp: str

    @classmethod
    def setUpClass(cls) -> None:
        cls._class_tmp = tempfile.mkdtemp()
        cls.system_bin = Path(cls._class_tmp) / "sys"
        build_system_bin(cls.system_bin)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls._class_tmp, ignore_errors=True)

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.bin / "tmux").symlink_to(shutil.which("tmux"))
        (self.bin / "workmux").symlink_to(STUBS / "workmux")
        (self.bin / "claude").symlink_to(STUBS / "claude")
        (self.tmp / "gitconfig").write_text("")
        self.workmux_log = self.tmp / "workmux.log"
        self.claude_log = self.tmp / "claude.log"
        self.workmux_log.touch()
        self.claude_log.touch()

        self.env = {key: value for key, value in os.environ.items() if key not in {"TMUX", "TMUX_PANE"}}
        self.env.update(
            PATH=f"{self.bin}:{self.system_bin}",
            TMUX_TMPDIR=tempfile.mkdtemp(),
            SHELL="/bin/sh",
            HOME=str(self.tmp),
            GIT_CONFIG_GLOBAL=str(self.tmp / "gitconfig"),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Test",
            GIT_AUTHOR_EMAIL="test@example.com",
            GIT_COMMITTER_NAME="Test",
            GIT_COMMITTER_EMAIL="test@example.com",
            STUB_WORKMUX_LOG=str(self.workmux_log),
            STUB_CLAUDE_LOG=str(self.claude_log),
        )
        self.addCleanup(shutil.rmtree, self.env["TMUX_TMPDIR"], ignore_errors=True)

        seed = self.tmp / "seed"
        self.origin = self.tmp / "origin.git"
        self.root = self.tmp / "repo"
        self.env["STUB_ROOT"] = str(self.root)
        self.git("init", "-q", "-b", "main", str(seed))
        (seed / "README.md").write_text("seed\n")
        self.git("-C", str(seed), "add", ".")
        self.git("-C", str(seed), "commit", "-q", "-m", "seed")
        self.git("clone", "-q", "--bare", str(seed), str(self.origin))
        self.git("clone", "-q", str(self.origin), str(self.root))
        self.seed = seed

        self.tmux("-f", "/dev/null", "new-session", "-d", "-x", "200", "-y", "50")
        self.addCleanup(self.run_tool, ["tmux", "kill-server"])
        self.window = self.tmux("list-windows", "-F", "#{window_id}").strip()
        socket = self.tmux("display-message", "-p", "#{socket_path}").strip()
        if not os.path.realpath(socket).startswith(os.path.realpath(self.env["TMUX_TMPDIR"]) + os.sep):
            self.fail(f"tmux would reach {socket}, outside the test's TMUX_TMPDIR")

    def run_tool(self, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(args, env=self.env, cwd=self.tmp, capture_output=True, text=True, check=check, timeout=30)

    def git(self, *args: str) -> str:
        return self.run_tool(["git", *args], check=True).stdout

    def tmux(self, *args: str) -> str:
        return self.run_tool(["tmux", *args], check=True).stdout

    def launch(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([str(LAUNCH), *args], env=env or self.env, cwd=self.root, capture_output=True, text=True, timeout=60)

    def c_locale(self) -> dict[str, str]:
        """Python gives its children LC_CTYPE=C.UTF-8 when the locale is C, so only an explicit environment reaches the launcher with no UTF-8 locale."""
        kept = {key: value for key, value in self.env.items() if key != "LANG" and not key.startswith("LC_")}
        return {**kept, "LC_ALL": "C"}

    def zoomed(self) -> str:
        return self.tmux("display-message", "-p", "-t", self.window, "#{window_zoomed_flag}").strip()

    def without(self, command: str, /) -> dict[str, str]:
        reduced = self.tmp / f"bin-without-{command}"
        reduced.mkdir(exist_ok=True)
        for entry in self.bin.iterdir():
            if entry.name != command and not (reduced / entry.name).exists():
                (reduced / entry.name).symlink_to(entry)
        return {**self.env, "PATH": f"{reduced}:{self.system_bin}"}

    def worktree(self, name: str) -> Path:
        return Path(f"{self.root}__wt/{name}")

    def make_worktree(self, *, name: str, base: str) -> Path:
        self.run_tool(["workmux", "add", name, "--headless", "--base", base], check=True)
        return self.worktree(name)

    def make_feature_worktree(self) -> Path:
        return self.make_worktree(name="f", base="origin/main")

    def commit_in(self, worktree: Path, *, relative: str) -> None:
        path = worktree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")
        self.git("-C", str(worktree), "add", relative)
        self.git("-C", str(worktree), "commit", "-q", "-m", relative)

    def panes(self) -> list[dict[str, str]]:
        out = self.tmux("list-panes", "-a", "-F", PANE_FORMAT)
        keys = ("id", "pid", "width", "height", "window")
        return [dict(zip(keys, line.split(), strict=True)) for line in out.splitlines()]

    def windows(self) -> list[str]:
        return self.tmux("list-windows", "-a", "-F", "#{window_id}").split()

    def processes(self) -> list[PsRow]:
        out = self.run_tool(["ps", "-A", "-o", "pid=,ppid=,args="], check=True).stdout
        rows = []
        for line in out.splitlines():
            parts = line.split(None, 2)
            if len(parts) == 3:
                rows.append(PsRow(pid=int(parts[0]), ppid=int(parts[1]), args=parts[2]))
        return rows

    def claude_processes(self) -> list[ClaudeProcess]:
        """Claude processes under the private server's panes, never the developer's own sessions."""
        rows = self.processes()
        parent = {row.pid: row.ppid for row in rows}
        pane_of_pid = {int(p["pid"]): p["id"] for p in self.panes()}
        found = []
        for row in rows:
            if os.path.basename(row.args.split()[0]) != "claude":
                continue
            current = row.pid
            while current > 1 and current not in pane_of_pid:
                current = parent.get(current, 0)
            if current in pane_of_pid:
                found.append(ClaudeProcess(pid=row.pid, args=row.args, pane=pane_of_pid[current]))
        return found

    def named_claudes(self, name: str, /) -> list[ClaudeProcess]:
        return [row for row in self.claude_processes() if f"--name {name}" in row.args]

    def claude_in_pane(self, pane: str, /) -> str | None:
        return next((row.args for row in self.claude_processes() if row.pane == pane), None)

    def wait_for(self, predicate: Callable[[], T], *, message: str) -> T:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(0.05)
        self.fail(message)

    def wait_for_claude(self, pane: str) -> str:
        return self.wait_for(lambda: self.claude_in_pane(pane), message=f"no claude started in {pane}")

    def kill_claude(self, name: str) -> None:
        for row in self.named_claudes(name):
            os.kill(row.pid, signal.SIGTERM)
        self.wait_for(lambda: not self.named_claudes(name), message=f"claude {name} did not exit")

    def make_pane(self, worktree: Path, *, command: str) -> str:
        pane = self.tmux("split-window", "-d", "-P", "-F", "#{pane_id}", "-t", self.window, "-c", str(worktree), command).strip()
        self.wait_for_claude(pane)
        return pane

    def started(self, result: subprocess.CompletedProcess, *, name: str) -> Started:
        self.assertEqual(result.returncode, 0, result.stderr)
        words = result.stdout.split()
        self.assertEqual(words[:2], ["started", name], result.stdout)
        return Started(pane=words[2].removeprefix("pane="), worktree=words[3].removeprefix("worktree="))

    def prompt_of(self, name: str) -> str:
        line = self.wait_for(lambda: next((l for l in self.claude_log.read_text().splitlines() if f"--name {name} " in l), None), message=f"claude {name} was not started")
        return line[line.index("/sam-mode"):]


class StartTests(LauncherTestCase):
    def test_first_spec_writer_opens_the_feature_window(self) -> None:
        before = self.windows()

        pane, worktree = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        new_windows = [w for w in self.windows() if w not in before]
        self.assertEqual(len(new_windows), 1)
        first_pane = next(p for p in self.panes() if p["window"] == new_windows[0])
        self.assertEqual(pane, first_pane["id"])
        self.assertIn("--name f-spec ", self.wait_for_claude(pane))
        self.assertEqual(Path(worktree), self.worktree("f"))
        self.assertIn("add f --base origin/main -C", self.workmux_log.read_text().splitlines())
        self.assertEqual(self.prompt_of("f-spec"), "/sam-mode spec feature=f phase=- update=- roadmap=- plan=- orchestrator=f-orchestrator")

    def test_first_spec_writer_finds_its_window_when_the_layout_opens_in_a_subdirectory(self) -> None:
        self.env["STUB_WORKMUX_START_DIR"] = "docs"
        before = self.windows()

        pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        new_windows = [w for w in self.windows() if w not in before]
        self.assertEqual([p["window"] for p in self.panes() if p["id"] == pane], new_windows)
        self.assertIn("--name f-spec ", self.wait_for_claude(pane))

    def test_phase_session_gets_a_pane_in_the_window_and_its_prompt(self) -> None:
        feature = self.make_feature_worktree()
        self.commit_in(feature, relative=f".foundry/feature-roadmaps/{ROADMAP_ID}/README.md")
        windows = self.windows()

        pane, worktree = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")

        self.assertEqual(next(p["window"] for p in self.panes() if p["id"] == pane), self.window)
        self.assertEqual(Path(worktree), self.worktree("f-phase-p"))
        self.assertEqual(self.windows(), windows)
        self.assertEqual(self.git("-C", worktree, "rev-parse", "HEAD"), self.git("-C", str(feature), "rev-parse", "HEAD"))
        self.assertIn("--name f-phase-p ", self.wait_for_claude(pane))
        self.assertEqual(
            self.prompt_of("f-phase-p"),
            f"/sam-mode phase feature=f phase=p update=- roadmap=.foundry/feature-roadmaps/{ROADMAP_ID} plan=.foundry/plans/{ROADMAP_ID}/README.md orchestrator=f-orchestrator",
        )

    def test_planner_and_update_spec_writer_names(self) -> None:
        self.make_feature_worktree()

        _, planner_worktree = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")
        _, update_worktree = self.started(self.launch("--feature", "f", "--role", "spec", "--update", "2", "--window", self.window), name="f-spec-2")

        self.assertEqual(Path(planner_worktree), self.worktree("f-planner"))
        self.assertEqual(Path(update_worktree), self.worktree("f-spec-2"))
        self.assertEqual(self.git("-C", update_worktree, "branch", "--show-current").strip(), "f-spec-2")
        self.assertTrue(self.prompt_of("f-planner").startswith("/sam-mode planner feature=f phase=- update=- "))
        self.assertTrue(self.prompt_of("f-spec-2").startswith("/sam-mode spec feature=f phase=- update=2 "))

    def test_second_launch_reports_alive_and_changes_nothing(self) -> None:
        self.make_feature_worktree()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        pane, _ = self.started(self.launch(*args), name="f-phase-p")
        self.wait_for_claude(pane)
        panes, windows = len(self.panes()), self.windows()

        result = self.launch(*args)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-phase-p pane={pane}\n"), result.stderr)
        self.assertEqual((len(self.panes()), self.windows()), (panes, windows))
        self.assertEqual(len(self.named_claudes("f-phase-p")), 1)

    def test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer(self) -> None:
        feature = self.make_feature_worktree()
        resurrected = self.make_pane(feature, command="claude --continue")
        panes = len(self.panes())

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={resurrected}\n"), result.stderr)
        self.assertEqual(len(self.panes()), panes)
        self.assertEqual(len(self.claude_processes()), 1)

        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec", "--window", self.window), name="f-spec")
        self.assertIn("--name f-spec ", self.wait_for_claude(spec))

    def test_a_name_later_in_the_arguments_is_not_the_session(self) -> None:
        self.make_feature_worktree()
        decoy = self.make_pane(self.tmp, command="claude --model m --continue say --name f-phase-p")
        args = ("--feature", "f", "--role", "phase", "--phase", "p")

        closed = self.launch(*args, "--close")

        self.assertEqual((closed.returncode, closed.stdout), (0, "absent f-phase-p\n"), closed.stderr)
        self.assertIn(decoy, [p["id"] for p in self.panes()])
        pane, _ = self.started(self.launch(*args, "--window", self.window), name="f-phase-p")
        self.assertIn("--name f-phase-p ", self.wait_for_claude(pane))

    def test_the_session_starts_whatever_the_default_shell(self) -> None:
        self.make_feature_worktree()
        self.tmux("set-option", "-g", "default-shell", "/usr/bin/false")

        pane, _ = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertIn("--name f-planner ", self.wait_for_claude(pane))

    def test_a_claude_named_for_the_session_is_alive_outside_its_worktree(self) -> None:
        self.make_feature_worktree()
        pane = self.make_pane(self.tmp, command="claude --name f-orchestrator")

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={pane}\n"), result.stderr)
        self.assertEqual(len(self.claude_processes()), 1)

    def test_restart_resumes_its_own_conversation_unless_fresh(self) -> None:
        self.make_feature_worktree()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        first, _ = self.started(self.launch(*args), name="f-phase-p")
        first_id = conversation(self.wait_for_claude(first), flag="--session-id")
        self.kill_claude("f-phase-p")

        resumed, _ = self.started(self.launch(*args), name="f-phase-p")
        self.assertNotEqual(resumed, first)
        resumed_args = self.wait_for_claude(resumed)
        self.assertEqual(conversation(resumed_args, flag="--resume"), first_id)
        self.assertIn(f"--name f-phase-p --resume {first_id} /sam-mode phase ", resumed_args)
        self.kill_claude("f-phase-p")

        fresh, _ = self.started(self.launch(*args, "--fresh"), name="f-phase-p")
        self.assertNotIn(conversation(self.wait_for_claude(fresh), flag="--session-id"), {first_id, None})

    def test_two_sessions_in_the_feature_worktree_keep_their_own_conversations(self) -> None:
        spec_pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = next(p["window"] for p in self.panes() if p["id"] == spec_pane)
        spec = ("--feature", "f", "--role", "spec", "--window", window)
        orchestrator = ("--feature", "f", "--role", "orchestrator", "--window", window)
        orchestrator_pane, _ = self.started(self.launch(*orchestrator), name="f-orchestrator")
        ids = {
            "f-spec": conversation(self.wait_for_claude(spec_pane), flag="--session-id"),
            "f-orchestrator": conversation(self.wait_for_claude(orchestrator_pane), flag="--session-id"),
        }
        self.assertNotEqual(ids["f-spec"], ids["f-orchestrator"])

        for order in ((orchestrator, spec), (spec, orchestrator)):
            self.kill_claude("f-spec")
            self.kill_claude("f-orchestrator")
            for args in order:
                name = f"f-{args[3]}"
                pane, _ = self.started(self.launch(*args), name=name)
                self.assertEqual(conversation(self.wait_for_claude(pane), flag="--resume"), ids[name], order)

    def test_panes_other_than_the_split_one_keep_their_size(self) -> None:
        self.make_feature_worktree()
        main = self.panes()[0]["id"]
        self.tmux("split-window", "-d", "-h", "-l", "20", "-t", main)
        self.tmux("split-window", "-d", "-v", "-l", "10", "-t", main)
        before = {p["id"]: (p["width"], p["height"]) for p in self.panes()}

        pane, _ = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        after = {p["id"]: (p["width"], p["height"]) for p in self.panes()}
        changed = [p for p in before if before[p] != after[p]]
        self.assertEqual(changed, [main])
        self.assertEqual(set(after) - set(before), {pane})

    def test_largest_session_pane_is_split(self) -> None:
        self.make_feature_worktree()
        main = self.panes()[0]["id"]
        large = self.tmux("split-window", "-d", "-P", "-F", "#{pane_id}", "-h", "-l", "40", "-t", main, "claude --name other-a").strip()
        small = self.tmux("split-window", "-d", "-P", "-F", "#{pane_id}", "-v", "-l", "15", "-t", large, "claude --name other-b").strip()
        self.wait_for_claude(large)
        self.wait_for_claude(small)
        before = {p["id"]: (p["width"], p["height"]) for p in self.panes()}

        self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        after = {p["id"]: (p["width"], p["height"]) for p in self.panes()}
        self.assertEqual([p for p in before if before[p] != after[p]], [large])

    def test_concurrent_launches_of_an_existing_worktree_start_one_copy(self) -> None:
        self.make_feature_worktree()
        self.make_worktree(name="f-planner", base="f")
        command = [str(LAUNCH), "--feature", "f", "--role", "planner", "--window", self.window]
        launches = [subprocess.Popen(command, env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outputs = [launch.communicate(timeout=60) for launch in launches]

        self.assertEqual([launch.returncode for launch in launches], [0, 0], outputs)
        self.assertEqual(sorted(stdout.split()[0] for stdout, _ in outputs), ["alive", "started"], outputs)
        self.wait_for(lambda: self.named_claudes("f-planner"), message="no f-planner claude started")
        self.assertEqual(len(self.named_claudes("f-planner")), 1)

    def test_a_zoomed_window_stays_zoomed(self) -> None:
        self.make_feature_worktree()
        main = self.panes()[0]["id"]
        self.tmux("split-window", "-d", "-h", "-l", "40", "-t", main)
        self.tmux("resize-pane", "-Z", "-t", main)
        size = next((p["width"], p["height"]) for p in self.panes() if p["id"] == main)

        self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertEqual(self.zoomed(), "1")
        self.assertEqual(next((p["width"], p["height"]) for p in self.panes() if p["id"] == main), size)

    def test_an_unzoomed_window_stays_unzoomed(self) -> None:
        self.make_feature_worktree()

        self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertEqual(self.zoomed(), "0")

    def test_full_window_exits_4_with_the_tmux_error(self) -> None:
        self.make_feature_worktree()
        self.tmux("new-session", "-d", "-s", "tiny", "-x", "2", "-y", "2")
        tiny = self.tmux("list-windows", "-t", "tiny", "-F", "#{window_id}").strip()

        result = self.launch("--feature", "f", "--role", "planner", "--window", tiny)

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("no space for", result.stderr)
        self.assertEqual(self.claude_processes(), [])

        retry, _ = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")
        self.assertIsNotNone(conversation(self.wait_for_claude(retry), flag="--session-id"))


class RoadmapTests(LauncherTestCase):
    def launch_planner(self) -> subprocess.CompletedProcess:
        return self.launch("--feature", "f", "--role", "planner", "--window", self.window)

    def test_no_roadmap_gives_dashes(self) -> None:
        self.make_feature_worktree()

        self.started(self.launch_planner(), name="f-planner")

        self.assertIn(" roadmap=- plan=- ", self.prompt_of("f-planner"))

    def test_two_matching_roadmaps_fail(self) -> None:
        feature = self.make_feature_worktree()
        self.commit_in(feature, relative=".foundry/feature-roadmaps/2026-11-20_21-37-12-f/README.md")
        self.commit_in(feature, relative=".foundry/feature-roadmaps/2026-11-21_08-00-00-f/README.md")

        result = self.launch_planner()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("2026-11-21_08-00-00-f", result.stderr)
        self.assertEqual(self.claude_processes(), [])

    def test_a_longer_feature_name_is_not_matched(self) -> None:
        self.run_tool(["workmux", "add", "stack", "--headless", "--base", "origin/main"], check=True)
        self.commit_in(self.worktree("stack"), relative=".foundry/feature-roadmaps/2026-11-20_21-37-12-s-stack/README.md")

        self.started(self.launch("--feature", "stack", "--role", "planner", "--window", self.window), name="stack-planner")

        self.assertIn(" roadmap=- plan=- ", self.prompt_of("stack-planner"))


class DefaultBranchTests(LauncherTestCase):
    def test_origin_head_names_the_base_and_is_fetched_first(self) -> None:
        self.git("-C", str(self.seed), "checkout", "-q", "-b", "trunk")
        self.git("-C", str(self.seed), "push", "-q", str(self.origin), "trunk")
        self.git("-C", str(self.root), "fetch", "-q", "origin")
        self.git("-C", str(self.root), "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        self.commit_in(self.seed, relative="later.txt")
        self.git("-C", str(self.seed), "push", "-q", str(self.origin), "trunk")
        latest = self.git("-C", str(self.seed), "rev-parse", "HEAD").strip()

        _, worktree = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        self.assertEqual(self.git("-C", worktree, "rev-parse", "HEAD").strip(), latest)

    def test_no_origin_head_and_no_gh_fails_naming_both(self) -> None:
        self.git("-C", str(self.root), "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")

        result = self.launch("--feature", "f", "--role", "spec")

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("git symbolic-ref", result.stderr)
        self.assertIn("gh repo view", result.stderr)


class ArgumentTests(LauncherTestCase):
    def test_missing_commands_exit_3_naming_them(self) -> None:
        for command in ("tmux", "workmux", "claude"):
            with self.subTest(command=command):
                result = self.launch("--feature", "f", "--role", "spec", env=self.without(command))
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertIn(command, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_close_and_remove_need_only_their_commands(self) -> None:
        self.make_feature_worktree()
        self.make_worktree(name="f-planner", base="f")
        no_claude = self.without("claude")
        self.assertEqual(self.launch("--feature", "f", "--role", "planner", "--close", env=no_claude).returncode, 0)
        removed = self.launch("--feature", "f", "--role", "planner", "--remove", env=no_claude)
        self.assertEqual(removed.returncode, 0, removed.stderr)
        no_workmux = self.without("workmux")
        self.assertEqual(self.launch("--feature", "f", "--role", "planner", "--close", env=no_workmux).returncode, 0)
        self.assertEqual(self.launch("--feature", "f", "--role", "planner", "--remove", env=no_workmux).returncode, 3)

    def test_each_argument_rule_is_a_usage_error(self) -> None:
        cases = [
            [],
            ["--bogus"],
            ["--feature"],
            ["--role", "spec"],
            ["--feature", "f"],
            ["--feature", "Bad_Name", "--role", "spec"],
            ["--feature", "f-", "--role", "spec"],
            ["--feature", "f", "--role", "wizard"],
            ["--feature", "f", "--role", "phase"],
            ["--feature", "f", "--role", "phase", "--phase", "Bad"],
            ["--feature", "f", "--role", "spec", "--phase", "p"],
            ["--feature", "f", "--role", "planner", "--update", "2"],
            ["--feature", "f", "--role", "spec", "--update", "0"],
            ["--feature", "f", "--role", "spec", "--update", "x"],
            ["--feature", "f", "--role", "planner", "--close", "--remove"],
            ["--feature", "f", "--role", "planner", "--close", "--fresh"],
            ["--feature", "f", "--role", "planner", "--close", "--window", "@0"],
            ["--feature", "f", "--role", "planner", "--remove", "--fresh"],
            ["--feature", "f", "--role", "planner", "--remove", "--window", "@0"],
            ["--feature", "f", "--role", "spec", "--remove"],
            ["--feature", "f", "--role", "orchestrator", "--remove"],
            ["--print-window", "--feature", "f"],
            ["--feature", "f", "--role", "planner"],
            ["--feature", "f", "--role", "orchestrator"],
            ["--feature", "a-phase-b", "--role", "spec"],
            ["--feature", "a-phase", "--role", "spec"],
            ["--feature", "a-planner", "--role", "spec"],
            ["--feature", "a-orchestrator", "--role", "spec"],
            ["--feature", "a-spec", "--role", "spec"],
            ["--feature", "a-spec-2", "--role", "spec"],
        ]
        for args in cases:
            with self.subTest(args=args):
                result = self.launch(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Usage:", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_a_feature_name_that_another_features_session_could_have_is_refused(self) -> None:
        self.make_feature_worktree()
        for feature, role, taken in (("a-phase", "planner", ("a", "phase", "planner")), ("query-planner", "spec", ("query", "planner", None))):
            with self.subTest(feature=feature):
                result = self.launch("--feature", feature, "--role", role, "--window", self.window)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Usage:", result.stderr)
                taken_feature, taken_role, taken_phase = taken
                self.run_tool(["workmux", "add", taken_feature, "--headless", "--base", "origin/main"], check=True)
                phase = ("--phase", taken_phase) if taken_phase else ()
                self.started(self.launch("--feature", taken_feature, "--role", taken_role, *phase, "--window", self.window), name=f"{taken_feature}-{taken_role}" + (f"-{taken_phase}" if taken_phase else ""))

    def test_restarting_the_spec_writer_needs_a_window(self) -> None:
        self.make_feature_worktree()

        result = self.launch("--feature", "f", "--role", "spec")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Usage:", result.stderr)


class PrintWindowTests(LauncherTestCase):
    def test_prints_the_window_of_the_calling_pane(self) -> None:
        pane = self.panes()[0]["id"]

        result = self.launch("--print-window", env={**self.env, "TMUX_PANE": pane})

        self.assertEqual((result.returncode, result.stdout), (0, f"window={self.window}\n"), result.stderr)

    def test_outside_tmux_exits_1(self) -> None:
        result = self.launch("--print-window")

        self.assertEqual(result.returncode, 1)
        self.assertIn("not inside tmux", result.stderr)

    def test_a_pane_that_no_longer_exists_exits_1_naming_it(self) -> None:
        result = self.launch("--print-window", env={**self.env, "TMUX_PANE": "%999"})

        self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
        self.assertIn("%999", result.stderr)

    def test_without_tmux_exits_3(self) -> None:
        result = self.launch("--print-window", env={**self.without("tmux"), "TMUX_PANE": "%0"})

        self.assertEqual(result.returncode, 3)
        self.assertIn("tmux", result.stderr)


class CloseTests(LauncherTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.make_feature_worktree()

    def test_closes_the_sessions_own_pane(self) -> None:
        pane, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")
        self.wait_for_claude(pane)

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, f"closed f-phase-p pane={pane}\n"), result.stderr)
        self.assertNotIn(pane, [p["id"] for p in self.panes()])

    def test_absent_when_no_tmux_server_runs(self) -> None:
        self.tmux("kill-server")

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, "absent f-phase-p\n"), result.stderr)

    def test_absent_when_only_another_session_runs(self) -> None:
        other, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "q", "--window", self.window), name="f-phase-q")
        self.wait_for_claude(other)

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, "absent f-phase-p\n"), result.stderr)
        self.assertIn(other, [p["id"] for p in self.panes()])

    def test_a_resumed_nameless_claude_is_not_closed(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        resumed = self.make_pane(worktree, command="claude --continue")

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, "absent f-phase-p\n"), result.stderr)
        self.assertIn(resumed, [p["id"] for p in self.panes()])


class RemoveTests(LauncherTestCase):
    args = ("--feature", "f", "--role", "phase", "--phase", "p")

    def setUp(self) -> None:
        super().setUp()
        self.make_feature_worktree()

    def assert_refused(self, reason: str, *, env: dict[str, str] | None = None) -> None:
        worktrees_before = self.git("-C", str(self.root), "worktree", "list", "--porcelain")

        result = self.launch(*self.args, "--remove", env=env)

        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith("refused f-phase-p: "), result.stderr)
        self.assertIn(reason, result.stderr)
        self.assertEqual(self.git("-C", str(self.root), "worktree", "list", "--porcelain"), worktrees_before)

    def test_removes_a_clean_merged_worktree_and_keeps_its_branch(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")

        result = self.launch(*self.args, "--remove")

        self.assertEqual((result.returncode, result.stdout), (0, f"removed f-phase-p worktree={worktree}\n"), result.stderr)
        self.assertFalse(worktree.exists())
        self.assertEqual(self.git("-C", str(self.root), "branch", "--list", "f-phase-p").strip(), "f-phase-p")

    def test_dirty_worktree_is_refused(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        (worktree / "untracked.txt").write_text("x\n")

        self.assert_refused("dirty")
        self.assertTrue(worktree.exists())

    def test_unmerged_branch_is_refused(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        self.commit_in(worktree, relative="work.txt")

        self.assert_refused("not merged into f")
        self.assertTrue(worktree.exists())

    def test_live_session_is_refused(self) -> None:
        pane, worktree = self.started(self.launch(*self.args, "--window", self.window), name="f-phase-p")
        self.wait_for_claude(pane)

        self.assert_refused(pane)
        self.assertTrue(Path(worktree).exists())

    def test_resumed_nameless_session_is_refused(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        pane = self.make_pane(worktree, command="claude --continue")

        self.assert_refused(pane)

    def test_removes_when_no_tmux_server_runs(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        self.tmux("kill-server")

        result = self.launch(*self.args, "--remove")

        self.assertEqual((result.returncode, result.stdout), (0, f"removed f-phase-p worktree={worktree}\n"), result.stderr)

    def test_commits_on_a_detached_head_are_refused(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        self.git("-C", str(worktree), "checkout", "-q", "--detach")
        self.commit_in(worktree, relative="work.txt")

        self.assert_refused("not merged into f")
        self.assertTrue(worktree.exists())

    def test_another_claude_under_the_worktree_is_refused(self) -> None:
        worktree = self.make_worktree(name="f-phase-p", base="f")
        (worktree / "sub").mkdir()
        pane = self.make_pane(worktree / "sub", command="claude --name someone-else")

        self.assert_refused(pane)

    def test_missing_worktree_is_refused(self) -> None:
        self.assert_refused("no such worktree")


class LocaleTests(LauncherTestCase):
    """A tmux client without a UTF-8 locale prints control characters in formats as underscores."""

    args = ("--feature", "f", "--role", "phase", "--phase", "p")

    def setUp(self) -> None:
        super().setUp()
        self.make_feature_worktree()
        self.pane, self.session_worktree = self.started(self.launch(*self.args, "--window", self.window), name="f-phase-p")
        self.wait_for_claude(self.pane)

    def test_a_live_session_is_alive(self) -> None:
        result = self.launch(*self.args, "--window", self.window, env=self.c_locale())

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-phase-p pane={self.pane}\n"), result.stderr)
        self.assertEqual(len(self.named_claudes("f-phase-p")), 1)

    def test_close_closes_the_live_session(self) -> None:
        result = self.launch(*self.args, "--close", env=self.c_locale())

        self.assertEqual((result.returncode, result.stdout), (0, f"closed f-phase-p pane={self.pane}\n"), result.stderr)

    def test_remove_refuses_a_live_session(self) -> None:
        result = self.launch(*self.args, "--remove", env=self.c_locale())

        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn(self.pane, result.stderr)
        self.assertTrue(Path(self.session_worktree).exists())


if __name__ == "__main__":
    unittest.main()
