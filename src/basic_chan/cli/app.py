"""basic_chan.cli.app — Unified CLI builder & router for all chan applications."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from rich.console import Console

from .formatter import print_banner, render_table
from ..scaffolding.project_gen import scaffold_chan_project


def build_cli_parser(chan_instance: Any) -> argparse.ArgumentParser:
    ident = chan_instance.identity
    parser = argparse.ArgumentParser(
        prog=ident.slug,
        description=f"🌸 {ident.name} ({ident.japanese_name}) — {ident.tagline}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: status
    cmd_status = subparsers.add_parser("status", help="Display operational status & health")
    cmd_status.set_defaults(func=_handle_status)

    # Command: sisters
    cmd_sisters = subparsers.add_parser("sisters", help="Dynamically discover and list sibling chans")
    cmd_sisters.set_defaults(func=_handle_sisters)

    # Command: tools
    cmd_tools = subparsers.add_parser("tools", help="List registered tools and schemas")
    cmd_tools.add_argument("--compact", action="store_true", help="Output token-efficient schemas for small LLMs")
    cmd_tools.set_defaults(func=_handle_tools)

    # Command: mcp
    cmd_mcp = subparsers.add_parser("mcp", help="Run official MCP stdio server for AI coding agents")
    cmd_mcp.set_defaults(func=_handle_mcp)

    # Command: manifest
    cmd_manifest = subparsers.add_parser("manifest", help="Export OpenClaw AppManager manifest.json")
    cmd_manifest.set_defaults(func=_handle_manifest)

    # Command: scaffold
    cmd_scaffold = subparsers.add_parser("scaffold", help="Generate a new standard-compliant -chan project")
    cmd_scaffold.add_argument("name", help="Name of the new chan (e.g. 'Shinobi-chan')")
    cmd_scaffold.add_argument("--slug", default="", help="Slug (defaults to kebab-case of name)")
    cmd_scaffold.add_argument("--out", default=".", help="Target output directory")
    cmd_scaffold.set_defaults(func=_handle_scaffold)

    return parser


def _handle_status(chan: Any, args: Any) -> None:
    chan.print_banner()
    sisters = chan.sisters.discover_all()
    rows = [
        ["Project Root", str(chan.root)],
        ["Version", chan.identity.version],
        ["Registered Tools", str(len(chan.tools))],
        ["Discovered Sisters", str(len(sisters))],
        ["Storage Vault", str(chan.vault.db_path)],
    ]
    render_table(chan.console, f"{chan.identity.name} Status", ["Attribute", "Value"], rows)


def _handle_sisters(chan: Any, args: Any) -> None:
    chan.print_banner()
    sisters = chan.sisters.discover_all()
    if not sisters:
        chan.console.print("[yellow]No sibling chans discovered in current environment.[/yellow]")
        return
    rows = [[s.name, s.slug, s.version, str(s.root_path or "-")] for s in sisters]
    render_table(chan.console, "Discovered Sister Chans", ["Name", "Slug", "Version", "Root Path"], rows)


def _handle_tools(chan: Any, args: Any) -> None:
    if args.compact:
        print(json.dumps(chan.tools.to_compact_schemas(), indent=2))
        return

    chan.print_banner()
    specs = chan.tools.list_specs()
    rows = [[s.name, s.description[:50], ", ".join([p.name for p in s.params]) or "-"] for s in specs]
    render_table(chan.console, "Registered Tool Capabilities", ["Tool Name", "Description", "Parameters"], rows)


def _handle_mcp(chan: Any, args: Any) -> None:
    chan.run_mcp_server()


def _handle_manifest(chan: Any, args: Any) -> None:
    manifest = chan.generate_manifest()
    print(json.dumps(manifest, indent=2))


def _handle_scaffold(chan: Any, args: Any) -> None:
    name = args.name
    slug = args.slug or name.lower().replace(" ", "-")
    out = scaffold_chan_project(name=name, slug=slug, target_dir=args.out)
    chan.console.print(f"[bold green]✓ Successfully scaffolded new chan project at:[/bold green] {out}")


def main() -> None:
    """CLI entrypoint for standalone basic-chan package."""
    from ..identity import ChanIdentity
    from ..base import BaseChan

    ident = ChanIdentity(
        name="Basic-chan",
        slug="basic-chan",
        japanese_name="ベーシック・ちゃん",
        tagline="Daemonless, agent-native foundational framework for the -chan ecosystem.",
    )

    class RootBasicChan(BaseChan):
        def initialize(self) -> None:
            pass

    chan = RootBasicChan(identity=ident)
    parser = build_cli_parser(chan)
    if len(sys.argv) == 1:
        chan.print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(chan, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
