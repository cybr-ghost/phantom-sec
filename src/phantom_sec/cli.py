"""Friendly command-line interface for Phantom Sec."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from phantom_sec import __version__
from phantom_sec.export_tools import export_history_csv, export_json
from phantom_sec.local_history import Store
from phantom_sec.module_workshop import validate_manifest, write_template
from phantom_sec.modules import get_modules, run_module

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phantom-sec",
        description="A beginner-friendly toolkit for defensive security and computer checks.",
        epilog="Tip: run 'phantom-sec' without a command to open the interactive menu.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list", help="Show all available tools")
    run = sub.add_parser("run", help="Run one built-in tool")
    run.add_argument("module_id", help="Tool ID shown by 'phantom-sec list'")
    run.add_argument("--path", help="File or folder path for file and disk tools")
    run.add_argument("--domain", help="Hostname for a DNS lookup")
    run.add_argument("--address", help="IP address for a reverse DNS lookup")
    workshop = sub.add_parser("validate-module", help="Check a module description file (does not run code)")
    workshop.add_argument("manifest", type=Path, help="Path to the JSON description file")
    create = sub.add_parser("create-module", help="Create a starter JSON description for a future module")
    create.add_argument("module_id", help="Unique ID, for example demo.sample")
    create.add_argument("name", help="Human-readable tool name")
    create.add_argument("--output", type=Path, default=Path("module.json"), help="Where to save the JSON file")
    history = sub.add_parser("history", help="Show your locally saved tool history")
    history.add_argument("--limit", type=int, default=20, help="Number of entries to show (maximum 500)")
    export = sub.add_parser("export-history", help="Save your local history as a JSON or CSV file")
    export.add_argument("format", choices=["json", "csv"], help="Export format")
    export.add_argument("--output", type=Path, required=True, help="Output file path")
    sub.add_parser("menu", help="Open the interactive tool menu")
    sub.add_parser("doctor", help="Check whether Phantom Sec is ready to use")
    settings = sub.add_parser("settings", help="View or change simple local preferences")
    settings.add_argument("action", choices=["show", "get", "set"], help="What to do")
    settings.add_argument("key", nargs="?", help="Preference name")
    settings.add_argument("value", nargs="?", help="New preference value (for set)")
    return parser


def show_modules() -> None:
    table = Table(title="Phantom Sec tools")
    table.add_column("Tool ID", style="cyan")
    table.add_column("Name")
    table.add_column("What it does")
    for module in get_modules():
        table.add_row(module.module_id, module.name, module.description)
    console.print(table)


def interactive_menu() -> None:
    console.print(f"\n[bold cyan]PHANTOM SEC[/bold cyan] [dim]v{__version__}[/dim]")
    console.print("Choose a tool by its ID. Type [bold]q[/bold] whenever you want to quit.")
    while True:
        show_modules()
        choice = Prompt.ask("Tool ID (or q to quit)", default="q").strip()
        if choice.lower() == "q":
            console.print("See you next time!")
            return
        module = next((item for item in get_modules() if item.module_id == choice), None)
        if module is None:
            console.print("[yellow]I couldn't find that tool. Copy an ID from the table and try again.[/yellow]")
            continue
        kwargs = {}
        if module.module_id.startswith(("file.", "system.disk")):
            kwargs["path"] = Prompt.ask("Local file or folder path")
        elif module.module_id == "network.dns":
            kwargs["domain"] = Prompt.ask("Hostname (example: example.com)")
        elif module.module_id == "network.reverse-dns":
            kwargs["address"] = Prompt.ask("IP address")
        try:
            result = run_module(choice, **kwargs)
            Store().record_run(choice, result)
            console.print_json(json.dumps(result, indent=2, default=str))
        except (ValueError, OSError) as exc:
            console.print(f"[red]That tool could not finish:[/red] {exc}")
        console.print()


def run_doctor() -> int:
    checks = [
        ("Python version", sys.version_info >= (3, 10), f"{sys.version_info.major}.{sys.version_info.minor}"),
        ("Phantom Sec package", True, __version__),
        ("Tool catalogue", len(get_modules()) == 12, f"{len(get_modules())} built-in tools found"),
    ]
    try:
        data_dir = Path.home() / ".local" / "share" / "phantom-sec"
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".write-check"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks.append(("Local history folder", True, str(data_dir)))
    except OSError as exc:
        checks.append(("Local history folder", False, str(exc)))
    table = Table(title="Phantom Sec health check")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")
    for name, passed, details in checks:
        table.add_row(name, "[green]OK[/green]" if passed else "[red]Needs attention[/red]", details)
    console.print(table)
    return 0 if all(passed for _, passed, _ in checks) else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in (None, "menu"):
        interactive_menu()
        return 0
    if args.command == "doctor":
        return run_doctor()
    if args.command == "settings":
        store = Store()
        if args.action == "show":
            console.print_json(json.dumps(store.all_settings(), indent=2))
            return 0
        if not args.key:
            console.print("[yellow]Please provide a preference name.[/yellow]")
            console.print("Example: phantom-sec settings get theme")
            return 2
        if args.action == "get":
            value = store.get_setting(args.key)
            if value is None:
                console.print(f"[yellow]No saved value for '{args.key}'.[/yellow]")
                return 1
            console.print(f"{args.key} = {value}")
            return 0
        if args.action == "set":
            if args.value is None:
                console.print("[yellow]Please provide a value to save.[/yellow]")
                console.print("Example: phantom-sec settings set theme dark")
                return 2
            store.set_setting(args.key, args.value)
            console.print(f"[green]Saved preference:[/green] {args.key} = {args.value}")
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
        console.print(f"[green]Description file created:[/green] {args.output}")
        return 0
    if args.command == "history":
        console.print_json(json.dumps(Store().history(args.limit), indent=2))
        return 0
    if args.command == "export-history":
        rows = Store().history(500)
        destination = (export_history_csv(rows, args.output) if args.format == "csv"
                       else export_json({"history": rows}, args.output))
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
