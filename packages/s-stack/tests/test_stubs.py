from __future__ import annotations

import os
import subprocess
import tempfile
import time
import unittest

from launcher_case import STUBS


class ClaudeStubTests(unittest.TestCase):
    def test_ps_shows_the_arguments_from_the_first_moment_it_shows_claude(self) -> None:
        """The launcher reads --name from ps, so a stub that hides it for a moment makes launches fail by chance."""
        with tempfile.NamedTemporaryFile() as log:
            stub = subprocess.Popen([str(STUBS / "claude"), "--name", "f-orchestrator"], env={**os.environ, "STUB_CLAUDE_LOG": log.name})
            self.addCleanup(stub.wait)
            self.addCleanup(stub.kill)
            deadline = time.monotonic() + 10
            title = ""
            while not title.startswith("claude") and time.monotonic() < deadline:
                title = subprocess.run(["ps", "-ww", "-o", "args=", "-p", str(stub.pid)], capture_output=True, text=True).stdout.strip()
            self.assertTrue(title.startswith("claude --name f-orchestrator"), title)


if __name__ == "__main__":
    unittest.main()
