"""basic_chan.git_diff.diff_scanner — Git diff line-level parser for PR & commit filtering."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Set


class GitDiffScanner:
    """Extracts modified line ranges per file from git diff."""

    @classmethod
    def get_changed_lines(cls, repo_dir: Path | str, base_ref: str = "HEAD~1") -> Dict[str, Set[int]]:
        """Parses git diff output against base_ref.
        Returns a mapping of absolute file path string -> set of 1-indexed changed line numbers.
        """
        changed: Dict[str, Set[int]] = {}
        root = Path(repo_dir).resolve()
        if not (root / ".git").exists():
            return changed

        # Validate base_ref to prevent argument injection
        if not re.match(r"^[a-zA-Z0-9_.~^/@{}:-]+$", base_ref):
            return changed

        try:
            res = subprocess.run(
                ["git", "diff", "--no-ext-diff", "-U0", base_ref],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if res.returncode != 0 or not res.stdout:
                return changed

            current_file: Optional[Path] = None
            for line in res.stdout.splitlines():
                if line.startswith("+++ b/"):
                    rel = line[6:].strip()
                    current_file = (root / rel).resolve()
                    if str(current_file) not in changed:
                        changed[str(current_file)] = set()
                elif line.startswith("@@ ") and current_file:
                    m = re.search(r"\+([0-9]+)(?:,([0-9]+))?", line)
                    if m:
                        start = int(m.group(1))
                        count = int(m.group(2)) if m.group(2) else 1
                        for ln in range(start, start + count):
                            changed[str(current_file)].add(ln)
        except Exception:
            pass

        return changed
