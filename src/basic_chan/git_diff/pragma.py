"""basic_chan.git_diff.pragma — Inline comment suppression parser."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Set


class PragmaParser:
    """Parses inline ignore comments e.g. '# chan-ignore' or '# kunoichi-ignore'."""

    @classmethod
    def get_suppressed_lines(cls, file_path: Path | str, chan_slug: str = "") -> Set[int]:
        p = Path(file_path)
        suppressed: Set[int] = set()
        if not p.exists() or not p.is_file():
            return suppressed

        # Matches: # chan-ignore, // chan-ignore, /* chan-ignore */, or slug-specific
        slug_prefix = chan_slug.replace("-chan", "").strip()
        pattern = re.compile(
            rf"(?:#|//|/\*)\s*(?:chan-ignore|{slug_prefix}-ignore)\b",
            re.IGNORECASE,
        )

        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            for idx, line in enumerate(lines, start=1):
                if pattern.search(line):
                    suppressed.add(idx)
                    # Often an ignore comment suppresses the next line
                    suppressed.add(idx + 1)
        except Exception:
            pass

        return suppressed
