from __future__ import annotations

import subprocess
import unittest

from launcher_case import LAUNCH, LauncherTestCase, Pane


class PlacementTests(LauncherTestCase):
    sidebar = False

    def setUp(self) -> None:
        super().setUp()
        self.make_feature_worktree()
        self.first = self.panes()[0].id
        if self.sidebar:
            self.sidebar_pane = self.add_sidebar()

    def start(self, *args: str, name: str, env: dict[str, str] | None = None) -> str:
        return self.started(self.launch("--feature", "f", *args, "--window", self.window, env=env), name=name).pane

    def assert_split(self, *, before: dict[str, Pane], target: str, new: str) -> Pane:
        """Only target was split: new is the one new pane and every other pane kept its id, size and position."""
        after = self.geometry()
        self.assertEqual(set(after) - set(before), {new})
        self.assertEqual({p: after.get(p) for p in before if p != target}, {p: g for p, g in before.items() if p != target})
        return after[new]

    def right_of(self, *, pane: str) -> int:
        g = self.geometry()[pane]
        return g.left + g.width - 1

    def assert_full_height_column(self, *, before: dict[str, Pane], orchestrator: str, new: str) -> Pane:
        """new spans the window's height right of the orchestrator's column, which alone gave up width."""
        after = self.geometry()
        self.assertEqual(set(after) - set(before), {new})
        column = before[orchestrator]
        height = int(self.tmux("display-message", "-p", "-t", self.window, "#{window_height}"))
        self.assertEqual((after[new].top, after[new].height), (0, height))
        self.assertGreater(after[new].left, self.right_of(pane=orchestrator))
        self.assertIn(after[orchestrator].width - after[new].width, (0, 1))
        for pane, g in before.items():
            if g.left >= column.left and g.left + g.width <= column.left + column.width:
                self.assertEqual(after[pane]._replace(width=0), g._replace(width=0), pane)
                self.assertEqual(after[pane].width, after[orchestrator].width, pane)
            else:
                self.assertEqual((after[pane].top, after[pane].width, after[pane].height), (g.top, g.width, g.height), pane)
                if g.left < column.left:
                    self.assertEqual(after[pane].left, g.left, pane)
        return after[new]

    def test_a_planner_opens_a_full_height_column_beside_a_shared_orchestrator_column(self) -> None:
        self.tmux("respawn-pane", "-k", "-t", self.first, "-c", str(self.worktree("f")), "claude --name f-spec")
        self.wait_for_claude(self.first)
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        developer = self.split(target=orchestrator, flags=["-v"])
        before = self.geometry()
        self.assertEqual({before[p].left for p in (self.first, orchestrator, developer)}, {before[orchestrator].left})

        planner = self.assert_full_height_column(before=before, orchestrator=orchestrator, new=self.start("--role", "planner", name="f-planner"))

        if self.sidebar:
            self.assertEqual(self.geometry()[self.sidebar_pane], before[self.sidebar_pane])
        before = self.geometry()
        new = self.assert_split(before=before, target=planner.id, new=self.start("--role", "phase", "--phase", "p", name="f-phase-p"))
        self.assertEqual((new.left, new.width), (planner.left, planner.width))

    def test_orchestrator_goes_under_the_first_spec_writer(self) -> None:
        spec = self.split(target=self.first, flags=["-h"], command="claude --name f-spec")
        before = self.geometry()

        new = self.assert_split(before=before, target=spec, new=self.start("--role", "orchestrator", name="f-orchestrator"))

        self.assertEqual((new.left, new.width), (before[spec].left, before[spec].width))
        self.assertGreater(new.top, before[spec].top)

    def test_orchestrator_without_a_spec_writer_goes_under_the_topmost_pane_of_the_first_column(self) -> None:
        self.split(target=self.first, flags=["-h"])
        lower = self.split(target=self.first, flags=["-v"])
        before = self.geometry()

        new = self.assert_split(before=before, target=self.first, new=self.start("--role", "orchestrator", name="f-orchestrator"))

        self.assertEqual(new.left, before[self.first].left)
        self.assertGreater(new.top, before[self.first].top)
        self.assertLess(new.top, before[lower].top)

    def test_a_planners_column_lands_right_of_a_developer_column_which_keeps_its_width(self) -> None:
        developer = self.split(target=self.window, flags=["-h", "-f", "-l", "30"])
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        before = self.geometry()

        new = self.assert_full_height_column(before=before, orchestrator=orchestrator, new=self.start("--role", "planner", name="f-planner"))

        self.assertGreater(new.left, self.right_of(pane=developer))

    def test_a_phase_splits_the_largest_session_pane_right_of_the_column_and_never_a_developer_pane(self) -> None:
        self.split(target=self.window, flags=["-h", "-f", "-l", "30"])
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        planner = self.start("--role", "planner", name="f-planner")
        phase_p = self.start("--role", "phase", "--phase", "p", name="f-phase-p")
        self.assertGreater(self.geometry()[phase_p].left, self.right_of(pane=orchestrator))
        self.tmux("resize-pane", "-t", phase_p, "-y", "5")
        before = self.geometry()

        new = self.assert_split(before=before, target=planner, new=self.start("--role", "phase", "--phase", "q", name="f-phase-q"))

        self.assertEqual((new.left, new.width), (before[planner].left, before[planner].width))
        self.assertGreater(new.top, before[planner].top)

    def test_a_session_pane_wide_enough_for_two_is_split_side_by_side(self) -> None:
        self.tmux("resize-window", "-t", self.window, "-x", "500", "-y", "50")
        self.start("--role", "orchestrator", name="f-orchestrator")
        planner = self.start("--role", "planner", name="f-planner")
        before = self.geometry()
        self.assertGreaterEqual(before[planner].width, 161)

        new = self.assert_split(before=before, target=planner, new=self.start("--role", "phase", "--phase", "p", name="f-phase-p"))

        self.assertGreater(new.left, before[planner].left)
        self.assertEqual((new.top, new.height), (before[planner].top, before[planner].height))

    def test_update_spec_writers_stack_under_the_orchestrator_above_a_developer_pane(self) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        developer = self.split(target=orchestrator, flags=["-v"])

        before = self.geometry()
        first = self.start("--role", "spec", "--update", "1", name="f-spec-1")
        new = self.assert_split(before=before, target=orchestrator, new=first)
        self.assertEqual(new.left, before[orchestrator].left)
        self.assertGreater(new.top, before[orchestrator].top)
        self.assertLess(new.top, before[developer].top)

        before = self.geometry()
        new = self.assert_split(before=before, target=first, new=self.start("--role", "spec", "--update", "2", name="f-spec-2"))
        self.assertGreater(new.top, before[first].top)
        self.assertLess(new.top, before[developer].top)

    def test_concurrent_launches_of_different_sessions_keep_the_orchestrator_column(self) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        phases = ("a", "b", "c")
        for phase in phases:
            self.make_worktree(name=f"f-phase-{phase}", base="f")
        commands = [[str(LAUNCH), "--feature", "f", "--role", "phase", "--phase", phase, "--window", self.window] for phase in phases]
        launches = [subprocess.Popen(command, env=self.env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for command in commands]
        results = []
        for launch in launches:
            stdout, stderr = launch.communicate(timeout=60)
            results.append(subprocess.CompletedProcess(launch.args, launch.returncode, stdout, stderr))

        new = [self.started(result, name=f"f-phase-{phase}").pane for result, phase in zip(results, phases, strict=True)]
        after = self.geometry()
        for pane in new:
            self.assertGreater(after[pane].left, self.right_of(pane=orchestrator))
            self.assertGreaterEqual(after[orchestrator].width, after[pane].width)

    def test_a_developer_pane_in_the_orchestrator_column_is_never_split_or_moved(self) -> None:
        developer = self.split(target=self.first, flags=["-v"])
        before = self.geometry()[developer]
        launches = [
            (("--role", "orchestrator"), "f-orchestrator"),
            (("--role", "planner"), "f-planner"),
            (("--role", "phase", "--phase", "p"), "f-phase-p"),
            (("--role", "spec", "--update", "1"), "f-spec-1"),
            (("--role", "spec"), "f-spec"),
        ]
        for args, name in launches:
            pane = self.start(*args, name=name)
            after = self.geometry()
            if name == "f-planner":
                before = before._replace(width=after[self.first].width)
            self.assertEqual(after.get(developer), before, name)
            self.assertNotEqual(pane, developer)

    def test_sessions_the_orchestrator_starts_need_its_pane_in_the_window(self) -> None:
        self.tmux("new-window", "-d", "-c", str(self.worktree("f")), "claude --name f-orchestrator")
        self.wait_for(lambda: self.named_claudes("f-orchestrator"), message="no orchestrator in the other window")
        launches = ((("--role", "planner"), "f-planner"), (("--role", "phase", "--phase", "p"), "f-phase-p"), (("--role", "spec", "--update", "1"), "f-spec-1"))
        for args, name in launches:
            with self.subTest(name=name):
                before = self.geometry()

                result = self.launch("--feature", "f", *args, "--window", self.window)

                self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
                self.assertIn(f"no f-orchestrator pane in {self.window}", result.stderr)
                self.assertEqual(self.geometry(), before)
                self.assertFalse(self.worktree(name).exists())
                self.assertEqual(self.git("-C", str(self.root), "branch", "--list", name), "")
        self.assertEqual(self.claude_processes(), self.named_claudes("f-orchestrator"))

    def test_a_resurrected_orchestrator_places_sessions_like_a_launched_one(self) -> None:
        self.mark_launched(self.worktree("f"), name="f-orchestrator")
        orchestrator = self.split(target=self.first, flags=["-v"], command="claude --continue")

        before = self.geometry()
        self.assert_full_height_column(before=before, orchestrator=orchestrator, new=self.start("--role", "phase", "--phase", "p", name="f-phase-p"))

        before = self.geometry()
        new = self.assert_split(before=before, target=orchestrator, new=self.start("--role", "spec", "--update", "1", name="f-spec-1"))
        self.assertEqual(new.left, before[orchestrator].left)
        self.assertGreater(new.top, before[orchestrator].top)

    def test_a_nameless_claude_in_a_tagged_pane_is_not_the_orchestrator(self) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        spec = self.start("--role", "spec", name="f-spec")
        self.kill_claude("f-spec")
        self.tmux("respawn-pane", "-k", "-t", spec, "-c", str(self.worktree("f")), "claude")
        self.wait_for_claude(spec)
        before = self.geometry()

        new = self.assert_split(before=before, target=orchestrator, new=self.start("--role", "planner", name="f-planner"))

        self.assertGreater(new.left, self.right_of(pane=orchestrator))

    def assert_phase_splits_the_planner_while_zoomed(self, *, zoomed: str) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        planner = self.start("--role", "planner", name="f-planner")
        before = self.geometry()
        pane = {"orchestrator": orchestrator, "planner": planner}[zoomed]
        self.tmux("resize-pane", "-Z", "-t", pane)

        new = self.start("--role", "phase", "--phase", "p", name="f-phase-p")

        self.assertEqual(self.zoomed(), "1")
        self.assertEqual(self.tmux("display-message", "-p", "-t", self.window, "#{pane_id}").strip(), pane)
        self.tmux("resize-pane", "-Z", "-t", pane)
        self.assert_split(before=before, target=planner, new=new)

    def test_a_zoomed_orchestrator_is_measured_unzoomed_and_stays_zoomed(self) -> None:
        self.assert_phase_splits_the_planner_while_zoomed(zoomed="orchestrator")

    def test_a_zoomed_session_pane_is_measured_unzoomed_and_stays_zoomed(self) -> None:
        self.assert_phase_splits_the_planner_while_zoomed(zoomed="planner")

    def test_placement_works_without_a_utf8_locale(self) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        before = self.geometry()

        self.assert_full_height_column(before=before, orchestrator=orchestrator, new=self.start("--role", "planner", name="f-planner", env=self.c_locale()))

    def test_a_developers_nameless_claude_under_the_named_orchestrator_does_not_hide_it(self) -> None:
        orchestrator = self.start("--role", "orchestrator", name="f-orchestrator")
        planner = self.start("--role", "planner", name="f-planner")
        self.split(target=orchestrator, flags=["-v"], command="claude")
        before = self.geometry()

        new = self.assert_split(before=before, target=planner, new=self.start("--role", "phase", "--phase", "p", name="f-phase-p"))

        self.assertGreater(new.left, self.right_of(pane=orchestrator))
        result = self.launch("--feature", "f", "--role", "orchestrator", "--window", self.window)
        self.assertEqual((result.returncode, result.stdout), (0, f"alive f-orchestrator pane={orchestrator}\n"), result.stderr)


class PlacementWithSidebarTests(PlacementTests):
    sidebar = True


if __name__ == "__main__":
    unittest.main()
