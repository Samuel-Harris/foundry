from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
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


class Pane(NamedTuple):
    id: str
    pid: int
    window: str
    left: int
    top: int
    width: int
    height: int


PANE_FORMAT = "#{pane_id} #{pane_pid} #{window_id} #{pane_left} #{pane_top} #{pane_width} #{pane_height}"


def conversation(*, args: str, flag: str) -> str | None:
    words = args.split()
    return words[words.index(flag) + 1] if flag in words else None


def build_system_bin(target: Path) -> None:
    """Every system tool except the ones a test must be able to remove."""
    target.mkdir()
    withheld = {"tmux", "workmux", "claude", "gh"}
    for directory in ("/usr/bin", "/bin"):
        for entry in os.listdir(directory):
            link = target / entry
            # A dangling link in /usr/bin would pass an exists() check and collide.
            if entry not in withheld and not os.path.lexists(link):
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
        # The launcher finds this server through TMUX_TMPDIR. The test itself names it with -S, so no call of its own can reach another server.
        self.socket = Path(self.env["TMUX_TMPDIR"]) / f"tmux-{os.getuid()}" / "default"
        self.socket.parent.mkdir(mode=0o700)

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
        self.addCleanup(self.run_tool, ["tmux", "-S", str(self.socket), "kill-server"])
        self.window = self.tmux("list-windows", "-F", "#{window_id}").strip()
        reached = self.run_tool(["tmux", "display-message", "-p", "#{socket_path}"], check=True).stdout.strip()
        if os.path.realpath(reached) != os.path.realpath(self.socket):
            self.fail(f"the launcher's tmux would reach {reached}, not the test's server {self.socket}")

    def run_tool(self, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(args, env=self.env, cwd=self.tmp, capture_output=True, text=True, check=check, timeout=30)

    def git(self, *args: str) -> str:
        return self.run_tool(["git", *args], check=True).stdout

    def tmux(self, *args: str) -> str:
        return self.run_tool(["tmux", "-S", str(self.socket), *args], check=True).stdout

    def launch(self, *args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([str(LAUNCH), *args], env=env or self.env, cwd=cwd or self.root, capture_output=True, text=True, timeout=60)

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

    def replace_stub(self, name: str, *, body: str) -> None:
        target = self.bin / name
        target.unlink()
        target.write_text(body)
        target.chmod(0o755)

    def mark_launched(self, worktree: Path, *, name: str) -> None:
        """The conversation marker the launcher writes once it has started <name> in <worktree>."""
        markers = Path(self.git("-C", str(worktree), "rev-parse", "--git-path", "s-stack-sessions").strip())
        if not markers.is_absolute():
            markers = worktree / markers
        markers.mkdir(parents=True, exist_ok=True)
        (markers / name).write_text("00000000-0000-4000-8000-000000000000\n")

    def lock_path(self, name: str) -> Path:
        common = Path(self.git("-C", str(self.root), "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
        return common / "s-stack-locks" / name

    def write_lock(self, name: str, *, record: str) -> Path:
        """The lock <name> as a launch holding it leaves it, recording "<pid> <start time>"."""
        lock = self.lock_path(name)
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.symlink_to(record)
        return lock

    def start_time(self, pid: int, /) -> str:
        """A process's start time as every launch records it."""
        out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], env={**self.env, "LC_ALL": "C", "TZ": "UTC"}, capture_output=True, text=True, check=True).stdout
        return " ".join(out.split())

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

    def panes(self) -> list[Pane]:
        rows = []
        for line in self.tmux("list-panes", "-a", "-F", PANE_FORMAT).splitlines():
            pane, pid, window, left, top, width, height = line.split()
            rows.append(Pane(id=pane, pid=int(pid), window=window, left=int(left), top=int(top), width=int(width), height=int(height)))
        return rows

    def pane_ids(self) -> list[str]:
        return [p.id for p in self.panes()]

    def window_of(self, pane: str, /) -> str:
        return next(p.window for p in self.panes() if p.id == pane)

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
        pane_of_pid = {p.pid: p.id for p in self.panes()}
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

    def make_orchestrator(self, feature: str = "f", /) -> str:
        """An orchestrator pane the launcher did not start, so it carries no tag."""
        return self.make_pane(self.worktree(feature), command=f"claude --name {feature}-orchestrator")

    def split(self, *, target: str, flags: list[str], command: str | None = None) -> str:
        """A pane the developer adds by hand, untagged."""
        cwd = ["-c", str(self.worktree("f"))] if self.worktree("f").is_dir() else []
        pane = self.tmux("split-window", "-d", "-P", "-F", "#{pane_id}", "-t", target, *cwd, *flags, *([command] if command else [])).strip()
        if command and command.startswith("claude"):
            self.wait_for_claude(pane)
        return pane

    def sidebar_program(self) -> Path:
        """A blocking program named workmux, which tmux reports as the sidebar's command."""
        program = self.tmp / "sidebar" / "workmux"
        if not program.exists():
            program.parent.mkdir()
            if sys.platform == "darwin":
                # macOS reports a script's interpreter, so copy sleep, and sign the copy or macOS kills it.
                shutil.copy(os.path.realpath(shutil.which("sleep", path=str(self.system_bin))), program)
                subprocess.run(["codesign", "-f", "-s", "-", str(program)], check=True, capture_output=True)
            else:
                # Linux tmux reports argv[0], which for a script is its interpreter, so name the interpreter workmux.
                # A copied sleep will not do: a multicall coreutils rejects the name.
                interpreter = self.tmp / "sidebar" / "bin" / "workmux"
                interpreter.parent.mkdir()
                interpreter.symlink_to(os.path.realpath(shutil.which("sh", path=str(self.system_bin))))
                program.write_text(f"#!{interpreter}\nread _\n")
                program.chmod(0o755)
        return program

    def add_sidebar(self) -> str:
        """A narrow, full-height leftmost pane whose foreground process is named workmux, as tmux reports the sidebar."""
        pane = self.tmux("split-window", "-d", "-h", "-b", "-f", "-l", "20", "-P", "-F", "#{pane_id}", "-t", self.window, f"exec {self.sidebar_program()} 86400").strip()
        self.wait_for(lambda: self.tmux("display-message", "-p", "-t", pane, "#{pane_current_command}").strip() == "workmux", message="the sidebar stub does not read as workmux")
        return pane

    def geometry(self) -> dict[str, Pane]:
        return {p.id: p for p in self.panes() if p.window == self.window}

    def tag_of(self, pane: str, /) -> str:
        return self.tmux("show-options", "-p", "-v", "-t", pane, "@s-stack-session").strip()

    def started(self, result: subprocess.CompletedProcess, *, name: str) -> Started:
        self.assertEqual(result.returncode, 0, result.stderr)
        words = result.stdout.split()
        self.assertEqual(words[:2], ["started", name], result.stdout)
        return Started(pane=words[2].removeprefix("pane="), worktree=words[3].removeprefix("worktree="))

    def prompt_of(self, name: str) -> str:
        line = self.wait_for(lambda: next((l for l in self.claude_log.read_text().splitlines() if f"--name {name} " in l), None), message=f"claude {name} was not started")
        return line[line.index("/sam-mode"):]
