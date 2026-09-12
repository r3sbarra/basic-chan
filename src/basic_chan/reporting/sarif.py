"""basic_chan.reporting.sarif — OASIS SARIF 2.1.0 report exporter."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def generate_sarif_report(
    tool_name: str,
    version: str,
    rules: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Builds an OASIS SARIF 2.1.0 compliant report dictionary."""
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": version,
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }
