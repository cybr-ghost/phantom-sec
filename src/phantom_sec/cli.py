"""Command-line interface for Phantom Sec."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from phantom_sec import __version__
from phantom_sec.modules import get_modules, run_module
from phantom_sec.reports import export_history_csv, export_json
from phantom_sec.storage import Store
from phantom_sec.workshop import validate_manifest, write_template

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phantom-sec", description="Defensive security toolkit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list", help="List built-in modules")
    run = sub.add_parser("run", help="Run a built-in read-only utility")
    run.add_argument("module_id", help="Module identifier")
    run.add_argument("--path", help="File or directory path")
    run.add_argument("--domain", help="Domain name for DNS lookup")
    run.add_argument("--address", help="IP address for reverse DNS")
    workshop = sub.add_parser("validate-module", help="Validate a manifest without executing it")
    workshop.add_argument("manifest", type=Path)
    create = sub.add_parser("create-module", help="Create a JSON module manifest template")
    create.add_argument("module_id")
    create.add_argument("name")
    create.add_argument("--output", type=Path, default=Path("module.json"))
    history = sub.add_parser("history", help="Show local module run history")
    history.add_argument("--limit", type=int, default=20)
    export = sub.add_parser("export-history", help="Export local history as JSON or CSV")
    export.add_argument("format", choices=["json", "csv"])
    export.add_argument("--output", type=Path, required=True)
    sub.add_parser("menu", help="Open the interactive module menu")
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
    console.print(f"\n[bold cyan]PHANTOM SEC[/bold cyan] [dim]v{__version__}[/dim]")
    show_modules()
    ids = [module.module_id for module in get_modules()]
    choice = Prompt.ask("Module ID (or q to quit)", default="q")
    if choice.lower() == "q":
        return
    if choice not in ids:
        console.print("[red]Unknown module ID. Use the exact ID shown in the catalogue.[/red]")
        return
    module = next(item for item in get_modules() if item.module_id == choice)
    kwargs = {}
    if "path" in module.module_id:
        kwargs["path"] = Prompt.ask("Local path")
    elif module.module_id == "network.dns":
        kwargs["domain"] = Prompt.ask("Hostname")
    elif module.module_id == "network.reverse-dns":
        kwargs["address"] = Prompt.ask("IP address")
    try:
        result = run_module(choice, **kwargs)
        Store().record_run(choice, result)
        console.print_json(json.dumps(result, indent=2, default=str))
    except (ValueError, OSError) as exc:
        console.print(f"[red]Error:[/red] {exc}")


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
    if args.command == "create-module":
        write_template(args.output, args.module_id, args.name)
        console.print(f"[green]Manifest template created:[/green] {args.output}")
        return 0
    if args.command == "history":
        console.print_json(json.dumps(Store().history(args.limit), indent=2))
        return 0
    if args.command == "export-history":
        rows = Store().history(500)
        if args.format == "csv":
            destination = export_history_csv(rows, args.output)
        else:
            destination = export_json({"history": rows}, args.output)
        console.print(f"[green]Exported:[/green] {destination}")
        return 0
    if args.command == "run":
        try:
            result = run_module(args.module_id, path=args.path, domain=args.domain,
                                address=args.address)
            Store().record_run(args.module_id, result)
        except (ValueError, OSError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            return 2
        console.print_json(json.dumps(result, indent=2, default=str))
        return 0
    return 2
