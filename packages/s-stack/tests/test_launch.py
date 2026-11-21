from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from launcher_case import LAUNCH, ROADMAP_ID, LauncherTestCase, conversation


class StartTests(LauncherTestCase):
    def test_first_spec_writer_opens_the_feature_window(self) -> None:
        before = self.windows()

        pane, worktree = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        new_windows = [w for w in self.windows() if w not in before]
        self.assertEqual(len(new_windows), 1)
        first_pane = next(p for p in self.panes() if p.window == new_windows[0])
        self.assertEqual(pane, first_pane.id)
        self.assertIn("--name f-spec ", self.wait_for_claude(pane))
        self.assertEqual(self.tag_of(pane), "f-spec")
        self.assertEqual(Path(worktree), self.worktree("f"))
        self.assertIn("add f --base origin/main -C", self.workmux_log.read_text().splitlines())
        self.assertEqual(self.prompt_of("f-spec"), "/sam-mode spec feature=f phase=- update=- roadmap=- plan=- orchestrator=f-orchestrator")

    def test_first_spec_writer_finds_its_window_when_the_layout_opens_in_a_subdirectory(self) -> None:
        self.env["STUB_WORKMUX_START_DIR"] = "docs"
        before = self.windows()

        pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")

        new_windows = [w for w in self.windows() if w not in before]
        self.assertEqual([self.window_of(pane)], new_windows)
        self.assertIn("--name f-spec ", self.wait_for_claude(pane))

    def test_phase_session_gets_a_pane_in_the_window_and_its_prompt(self) -> None:
        feature = self.make_feature_worktree()
        self.commit_in(feature, relative=f".foundry/feature-roadmaps/{ROADMAP_ID}/README.md")
        self.make_orchestrator()
        windows = self.windows()

        pane, worktree = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")

        self.assertEqual(self.window_of(pane), self.window)
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
        self.make_orchestrator()

        _, planner_worktree = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")
        _, update_worktree = self.started(self.launch("--feature", "f", "--role", "spec", "--update", "2", "--window", self.window), name="f-spec-2")

        self.assertEqual(Path(planner_worktree), self.worktree("f-planner"))
        self.assertEqual(Path(update_worktree), self.worktree("f-spec-2"))
        self.assertEqual(self.git("-C", update_worktree, "branch", "--show-current").strip(), "f-spec-2")
        self.assertTrue(self.prompt_of("f-planner").startswith("/sam-mode planner feature=f phase=- update=- "))
        self.assertTrue(self.prompt_of("f-spec-2").startswith("/sam-mode spec feature=f phase=- update=2 "))

    def test_second_launch_reports_alive_and_changes_nothing(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
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
        self.mark_launched(feature, name="f-orchestrator")
        resurrected = self.make_pane(feature, command="claude --continue")
        panes = len(self.panes())

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={resurrected}\n"), result.stderr)
        self.assertEqual(len(self.panes()), panes)
        self.assertEqual(len(self.claude_processes()), 1)

        spec, _ = self.started(self.launch("--feature", "f", "--role", "spec", "--window", self.window), name="f-spec")
        self.assertIn("--name f-spec ", self.wait_for_claude(spec))

    def test_a_plain_claude_in_the_feature_worktree_is_not_an_orchestrator_never_launched(self) -> None:
        feature = self.make_feature_worktree()
        plain = self.make_pane(feature, command="claude")

        pane, _ = self.started(self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window), name="f-orchestrator")

        self.assertIn("--name f-orchestrator ", self.wait_for_claude(pane))
        self.assertEqual((self.claude_in_pane(plain) or "").split(), ["claude"])

    def test_a_name_later_in_the_arguments_is_not_the_session(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        decoy = self.make_pane(self.tmp, command="claude --model m --continue say --name f-phase-p")
        args = ("--feature", "f", "--role", "phase", "--phase", "p")

        closed = self.launch(*args, "--close")

        self.assertEqual((closed.returncode, closed.stdout), (0, "absent f-phase-p\n"), closed.stderr)
        self.assertIn(decoy, self.pane_ids())
        pane, _ = self.started(self.launch(*args, "--window", self.window), name="f-phase-p")
        self.assertIn("--name f-phase-p ", self.wait_for_claude(pane))

    def test_the_session_starts_whatever_the_default_shell(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        self.tmux("set-option", "-g", "default-shell", "/usr/bin/false")

        pane, _ = self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertIn("--name f-planner ", self.wait_for_claude(pane))

    def test_a_claude_named_for_the_session_is_alive_outside_its_worktree(self) -> None:
        self.make_feature_worktree()
        pane = self.make_pane(self.tmp, command="claude --name f-orchestrator")

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={pane}\n"), result.stderr)
        self.assertEqual(len(self.claude_processes()), 1)

    def test_a_claude_resumed_by_hand_in_the_sessions_own_pane_is_alive(self) -> None:
        spec_pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = self.window_of(spec_pane)
        orchestrator = ("--feature", "f", "--role", "orchestrator", "--window", window)
        pane, _ = self.started(self.launch(*orchestrator), name="f-orchestrator")
        self.wait_for_claude(pane)
        self.kill_claude("f-orchestrator")
        self.tmux("respawn-pane", "-k", "-t", pane, "-c", str(self.worktree("f")), "claude --continue")
        self.wait_for_claude(pane)

        result = self.launch(*orchestrator)

        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={pane}\n"), result.stderr)

    def test_restart_resumes_its_own_conversation_unless_fresh(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        first, _ = self.started(self.launch(*args), name="f-phase-p")
        first_id = conversation(args=self.wait_for_claude(first), flag="--session-id")
        self.kill_claude("f-phase-p")

        resumed, _ = self.started(self.launch(*args), name="f-phase-p")
        resumed_args = self.wait_for_claude(resumed)
        self.assertEqual(conversation(args=resumed_args, flag="--resume"), first_id)
        self.assertIn(f"--name f-phase-p --resume {first_id} /sam-mode phase ", resumed_args)
        self.kill_claude("f-phase-p")

        fresh, _ = self.started(self.launch(*args, "--fresh"), name="f-phase-p")
        self.assertNotIn(conversation(args=self.wait_for_claude(fresh), flag="--session-id"), {first_id, None})

    def test_two_sessions_in_the_feature_worktree_keep_their_own_conversations(self) -> None:
        spec_pane, _ = self.started(self.launch("--feature", "f", "--role", "spec"), name="f-spec")
        window = self.window_of(spec_pane)
        spec = ("--feature", "f", "--role", "spec", "--window", window)
        orchestrator = ("--feature", "f", "--role", "orchestrator", "--window", window)
        orchestrator_pane, _ = self.started(self.launch(*orchestrator), name="f-orchestrator")
        ids = {
            "f-spec": conversation(args=self.wait_for_claude(spec_pane), flag="--session-id"),
            "f-orchestrator": conversation(args=self.wait_for_claude(orchestrator_pane), flag="--session-id"),
        }
        self.assertNotEqual(ids["f-spec"], ids["f-orchestrator"])

        panes = {"f-spec": spec_pane, "f-orchestrator": orchestrator_pane}
        launches = {"f-spec": spec, "f-orchestrator": orchestrator}
        for order in (("f-orchestrator", "f-spec"), ("f-spec", "f-orchestrator")):
            self.kill_claude("f-spec")
            self.kill_claude("f-orchestrator")
            for name in order:
                pane, _ = self.started(self.launch(*launches[name]), name=name)
                self.assertEqual(pane, panes[name], order)
                self.assertEqual(conversation(args=self.wait_for_claude(pane), flag="--resume"), ids[name], order)

    def test_a_restart_reuses_the_sessions_own_pane(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        first, _ = self.started(self.launch(*args), name="f-phase-p")
        first_id = conversation(args=self.wait_for_claude(first), flag="--session-id")
        self.kill_claude("f-phase-p")
        panes = len(self.panes())

        restarted, _ = self.started(self.launch(*args), name="f-phase-p")

        self.assertEqual(restarted, first)
        self.assertEqual(len(self.panes()), panes)
        self.assertEqual(self.tag_of(restarted), "f-phase-p")
        self.assertEqual(conversation(args=self.wait_for_claude(restarted), flag="--resume"), first_id)
        (running,) = self.named_claudes("f-phase-p")

        again = self.launch(*args)

        self.assertEqual((again.returncode, again.stdout), (0, f"alive f-phase-p pane={first}\n"), again.stderr)
        self.assertEqual(self.named_claudes("f-phase-p"), [running])

    def test_a_command_running_in_the_sessions_own_pane_is_never_killed(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        first, _ = self.started(self.launch(*args), name="f-phase-p")
        self.wait_for_claude(first)
        self.kill_claude("f-phase-p")
        self.tmux("send-keys", "-t", first, "sleep 98765", "Enter")
        busy = lambda: [row for row in self.processes() if row.args == "sleep 98765"]
        self.wait_for(busy, message="the developer's command did not start")

        restarted, _ = self.started(self.launch(*args), name="f-phase-p")

        self.assertNotEqual(restarted, first)
        self.assertIn("--name f-phase-p ", self.wait_for_claude(restarted))
        self.assertTrue(busy(), "the developer's command was killed")

    def test_ten_restarts_keep_the_pane_count(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        args = ("--feature", "f", "--role", "planner", "--window", self.window)
        pane, _ = self.started(self.launch(*args), name="f-planner")
        self.wait_for_claude(pane)
        panes = len(self.panes())

        for restart in range(10):
            self.kill_claude("f-planner")
            self.assertEqual(self.started(self.launch(*args), name="f-planner").pane, pane, restart)
            self.wait_for_claude(pane)

        self.assertEqual(len(self.panes()), panes)

    def test_a_pane_left_by_another_session_is_never_reused(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        other, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "q", "--window", self.window), name="f-phase-q")
        self.wait_for_claude(other)
        self.kill_claude("f-phase-q")

        pane, _ = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window), name="f-phase-p")

        self.assertNotEqual(pane, other)
        self.assertIn("--name f-phase-p ", self.wait_for_claude(pane))
        self.assertIn(other, self.pane_ids())
        self.assertIsNone(self.claude_in_pane(other))

    def test_a_tagged_pane_with_a_claude_running_is_never_reused(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()
        args = ("--feature", "f", "--role", "phase", "--phase", "p", "--window", self.window)
        occupied, _ = self.started(self.launch(*args), name="f-phase-p")
        self.wait_for_claude(occupied)
        self.kill_claude("f-phase-p")
        self.tmux("respawn-pane", "-k", "-t", occupied, "claude --name someone-else")
        self.wait_for_claude(occupied)

        pane, _ = self.started(self.launch(*args), name="f-phase-p")

        self.assertNotEqual(pane, occupied)
        self.assertIn("--name someone-else", self.claude_in_pane(occupied) or "")

    def test_concurrent_launches_of_an_existing_worktree_start_one_copy(self) -> None:
        self.make_feature_worktree()
        self.make_worktree(name="f-planner", base="f")
        self.make_orchestrator()
        self.tmux("set-environment", "-g", "STUB_CLAUDE_DELAY", "0.5")
        command = [str(LAUNCH), "--feature", "f", "--role", "planner", "--window", self.window]
        launches = [subprocess.Popen(command, env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outputs = [launch.communicate(timeout=60) for launch in launches]

        self.assertEqual([launch.returncode for launch in launches], [0, 0], outputs)
        self.assertEqual(sorted(stdout.split()[0] for stdout, _ in outputs), ["alive", "started"], outputs)
        self.wait_for(lambda: self.named_claudes("f-planner"), message="no f-planner claude started")
        self.assertEqual(len(self.named_claudes("f-planner")), 1)

    def test_a_zoomed_window_stays_zoomed(self) -> None:
        self.make_feature_worktree()
        main = self.panes()[0].id
        self.make_orchestrator()
        self.tmux("resize-pane", "-Z", "-t", main)
        size = self.geometry()[main]

        self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertEqual(self.zoomed(), "1")
        self.assertEqual(self.geometry()[main], size)

    def test_a_failed_split_leaves_a_zoomed_window_zoomed(self) -> None:
        self.make_feature_worktree()
        self.tmux("new-session", "-d", "-s", "tiny", "-x", "4", "-y", "5")
        tiny = self.tmux("list-windows", "-t", "tiny", "-F", "#{window_id}").strip()
        top = self.tmux("list-panes", "-t", tiny, "-F", "#{pane_id}").strip()
        self.tmux("split-window", "-d", "-v", "-t", top)
        self.tmux("resize-pane", "-Z", "-t", top)

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", tiny)

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertEqual(self.tmux("display-message", "-p", "-t", top, "#{window_zoomed_flag} #{pane_active}").strip(), "1 1")

    def test_an_unzoomed_window_stays_unzoomed(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()

        self.started(self.launch("--feature", "f", "--role", "planner", "--window", self.window), name="f-planner")

        self.assertEqual(self.zoomed(), "0")

    def test_full_window_exits_4_with_the_tmux_error(self) -> None:
        self.make_feature_worktree()
        self.tmux("new-session", "-d", "-s", "tiny", "-x", "2", "-y", "2")
        tiny = self.tmux("list-windows", "-t", "tiny", "-F", "#{window_id}").strip()

        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", tiny)

        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("no space for", result.stderr)
        self.assertEqual(self.claude_processes(), [])

        retry, _ = self.started(self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window), name="f-orchestrator")
        self.assertIsNotNone(conversation(args=self.wait_for_claude(retry), flag="--session-id"))


class RoadmapTests(LauncherTestCase):
    def launch_planner(self) -> subprocess.CompletedProcess:
        return self.launch("--feature", "f", "--role", "planner", "--window", self.window)

    def test_no_roadmap_gives_dashes(self) -> None:
        self.make_feature_worktree()
        self.make_orchestrator()

        self.started(self.launch_planner(), name="f-planner")

        self.assertIn(" roadmap=- plan=- ", self.prompt_of("f-planner"))

    def test_two_matching_roadmaps_fail(self) -> None:
        feature = self.make_feature_worktree()
        self.commit_in(feature, relative=".foundry/feature-roadmaps/2026-11-20_21-37-12-f/README.md")
        self.commit_in(feature, relative=".foundry/feature-roadmaps/2026-11-21_08-00-00-f/README.md")
        self.make_orchestrator()

        result = self.launch_planner()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("2026-11-21_08-00-00-f", result.stderr)
        self.assertEqual(self.named_claudes("f-planner"), [])

    def test_a_longer_feature_name_is_not_matched(self) -> None:
        self.run_tool(["workmux", "add", "stack", "--headless", "--base", "origin/main"], check=True)
        self.commit_in(self.worktree("stack"), relative=".foundry/feature-roadmaps/2026-11-20_21-37-12-s-stack/README.md")
        self.make_orchestrator("stack")

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
                self.make_orchestrator(taken_feature)
                phase = ("--phase", taken_phase) if taken_phase else ()
                self.started(self.launch("--feature", taken_feature, "--role", taken_role, *phase, "--window", self.window), name=f"{taken_feature}-{taken_role}" + (f"-{taken_phase}" if taken_phase else ""))

    def test_restarting_the_spec_writer_needs_a_window(self) -> None:
        self.make_feature_worktree()

        result = self.launch("--feature", "f", "--role", "spec")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
