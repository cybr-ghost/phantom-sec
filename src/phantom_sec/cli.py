"""Command-line interface for Phantom Sec."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from phantom_sec import __version__
from phantom_sec.modules import get_modules, run_module
from phantom_sec.workshop import validate_manifest

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phantom-sec", description="Defensive security toolkit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list", help="List built-in modules")
    run = sub.add_parser("run", help="Run a built-in read-only utility")
    run.add_argument("module_id", help="Module identifier")
    run.add_argument("--path", help="File or directory path for file-analysis modules")
    run.add_argument("--domain", help="Domain name for DNS lookup")
    sub.add_parser("menu", help="Show the interactive module menu")
    workshop = sub.add_parser("validate-module", help="Validate a module manifest without executing it")
    workshop.add_argument("manifest", type=Path)
    return parser


def show_modules() -> None:
    table = Table(title="Phantom Sec modules")
    table.add_column("ID", style="cyan")
    table.add_column("Category")
    table.add_column("Description")
    for module in get_modules():
        table.add_row(module.module_id, module.category, module.description)
    console.print(table)


def interactive_menu() -> None:
    show_modules()
    console.print("\nRun a module with: [bold]phantom-sec run MODULE_ID[/bold]")
    console.print("Use --help to see available options.")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in (None, "menu"):
        interactive_menu()
        return 0
    if args.command == "list":
        show_modules()
        return 0
    if args.command == "validate-module":
        result = validate_manifest(args.manifest)
        console.print_json(json.dumps(result, indent=2))
        return 0 if result["valid"] else 2
    if args.command == "run":
        try:
            result = run_module(args.module_id, path=args.path, domain=args.domain)
        except (ValueError, OSError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            return 2
        console.print_json(json.dumps(result, indent=2, default=str))
        return 0
    return 2
