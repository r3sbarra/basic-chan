"""basic_chan.openclaw.manifest_gen — OpenClaw AppManager manifest generator & validator."""

from __future__ import annotations

from typing import Any, Dict, List


def generate_openclaw_manifest(
    name: str,
    slug: str,
    version: str,
    description: str,
    entry_point: str = "cli:main",
    has_web_ui: bool = False,
    settings: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "name": name,
        "slug": slug,
        "version": version,
        "description": description,
        "author": "OpenClaw",
        "entry_point": entry_point,
        "health_check_path": "/health",
        "app_type": "standalone",
        "has_web_ui": has_web_ui,
        "requires_auth": False,
        "settings": settings or [],
    }
