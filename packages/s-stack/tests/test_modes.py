from __future__ import annotations

import unittest
from pathlib import Path

from launcher_case import LauncherTestCase


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
        self.make_orchestrator()

    def test_closes_the_sessions_own_pane(self) -> None:
        pane, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")
        self.wait_for_claude(pane)

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, f"closed f-phase-p pane={pane}\n"), result.stderr)
        self.assertNotIn(pane, [p["id"] for p in self.panes()])

    def test_closes_the_sessions_pane_after_its_claude_exits(self) -> None:
        pane, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")
        self.wait_for_claude(pane)
        self.kill_claude("f-phase-p")

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, f"closed f-phase-p pane={pane}\n"), result.stderr)
        self.assertNotIn(pane, [p["id"] for p in self.panes()])

    def test_closes_both_the_sessions_left_pane_and_a_pane_running_it(self) -> None:
        left, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")
        self.wait_for_claude(left)
        self.kill_claude("f-phase-p")
        running = self.make_pane(self.tmp, command="claude --name f-phase-p")

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(result.stdout.splitlines()), sorted([f"closed f-phase-p pane={left}", f"closed f-phase-p pane={running}"]))
        self.assertFalse({left, running} & {p["id"] for p in self.panes()})

    def test_a_pane_left_by_another_session_is_not_closed(self) -> None:
        other, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "q", "--window", self.window), name="f-phase-q")
        self.wait_for_claude(other)
        self.kill_claude("f-phase-q")

        result = self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--close")

        self.assertEqual((result.returncode, result.stdout), (0, "absent f-phase-p\n"), result.stderr)
        self.assertIn(other, [p["id"] for p in self.panes()])

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
        self.make_orchestrator()

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
        self.make_orchestrator()
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
