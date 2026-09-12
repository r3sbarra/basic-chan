"""basic_chan.scaffolding.project_gen — Complete -chan project scaffolder."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .scripts_gen import generate_install_sh, generate_setup_sh, generate_start_sh


def scaffold_chan_project(
    name: str,
    slug: str,
    target_dir: Path | str,
    japanese_name: str = "",
    tagline: str = "",
) -> Path:
    """Creates a standard, fully-formed -chan application directory structure."""
    out = Path(target_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    pkg_name = slug.replace("-", "_")
    src_dir = out / "src" / pkg_name
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir = out / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (out / "data").mkdir(exist_ok=True)
    (out / "reports").mkdir(exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)

    # 1. Standard Scripts
    install_content = generate_install_sh(name, slug)
    setup_content = generate_setup_sh(name, slug)
    start_content = generate_start_sh(name, slug)

    (out / "install.sh").write_text(install_content, encoding="utf-8")
    (out / "setup.sh").write_text(setup_content, encoding="utf-8")
    (out / "start.sh").write_text(start_content, encoding="utf-8")

    for s in ("install.sh", "setup.sh", "start.sh"):
        (out / s).chmod(0o755)

    # 2. pyproject.toml
    pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = "{tagline or name}"
readme = "README.md"
authors = [{{ name = "OpenClaw", email = "ai@openclaw.local" }}]
license = {{ text = "MIT" }}
requires-python = ">=3.10"
dependencies = [
    "basic-chan>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]

[project.scripts]
{slug} = "{pkg_name}.cli.app:main"

[tool.setuptools.packages.find]
where = ["src"]
"""
    (out / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

    # 3. README.md
    readme_content = f"""# {name} ({japanese_name})

> **{tagline}**

## Quick Start
```bash
./install.sh
./setup.sh
./start.sh
```
"""
    (out / "README.md").write_text(readme_content, encoding="utf-8")

    # 4. Source package skeleton
    init_content = f"""from basic_chan import BaseChan, ChanIdentity

IDENTITY = ChanIdentity(
    name="{name}",
    slug="{slug}",
    japanese_name="{japanese_name}",
    tagline="{tagline}",
)

class {name.replace('-', '').replace(' ', '')}Chan(BaseChan):
    def __init__(self):
        super().__init__(identity=IDENTITY)

    def initialize(self) -> None:
        pass
"""
    (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")
    (src_dir / "cli").mkdir(exist_ok=True)
    cli_content = f"""from basic_chan.cli.app import build_cli_parser
from {pkg_name} import {name.replace('-', '').replace(' ', '')}Chan

def main():
    chan = {name.replace('-', '').replace(' ', '')}Chan()
    parser = build_cli_parser(chan)
    args = parser.parse_args()
    args.func(chan, args)

if __name__ == "__main__":
    main()
"""
    (src_dir / "cli" / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "cli" / "app.py").write_text(cli_content, encoding="utf-8")

    # 5. Basic test
    test_content = f"""from {pkg_name} import {name.replace('-', '').replace(' ', '')}Chan

def test_initialization():
    chan = {name.replace('-', '').replace(' ', '')}Chan()
    assert chan.identity.slug == "{slug}"
"""
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "test_core.py").write_text(test_content, encoding="utf-8")

    return out
