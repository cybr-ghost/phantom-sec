"""Retro terminal desktop interface for Phantom Sec.

The catalogue and individual tool sessions share one window. Built-in tools run
through their registered handlers; the input box is a tool parameter, not a shell.
"""

import json
import queue
import threading
import typing
from __future__ import annotations

from phantom_sec import __version__
from phantom_sec.local_history import Store
from phantom_sec.modules import Module, get_modules, run_module


BLACK = "#080808"
PANEL = "#111111"
WHITE = "#eeeeee"
GREY = "#999999"
DIM = "#666666"
RED = "#ed3038"
FONT = ("Cascadia Mono", 10)
FONT_BOLD = ("Cascadia Mono", 10, "bold")


def search_modules(query: str = "", category: str = "All tools") -> list[Module]:
    """Filter the catalogue by name, ID, description, and category."""
    needle = query.casefold().strip()
    return [
        module for module in get_modules()
        if (category == "All tools" or module.category == category)
        and (
            not needle
            or needle in module.module_id.casefold()
            or needle in module.name.casefold()
            or needle in module.description.casefold()
            or needle in module.category.casefold()
        )
    ]


def dashboard_summary(store: Store) -> dict[str, typing.Any]:
    """Return local catalogue and activity statistics."""
    modules = get_modules()
    recent = store.history(1)
    return {
        "tool_count": len(modules),
        "category_count": len({module.category for module in modules}),
        "recent_run": recent[0] if recent else None,
        "favorite_count": len(store.favorites()),
    }


def input_kind(module_id: str) -> str | None:
    """Return the single parameter required by a built-in tool, if any."""
    if module_id.startswith("file.") or module_id == "system.disk":
        return "path"
    if module_id == "network.dns" or module_id.startswith("domain."):
        return "domain"
    if module_id == "network.reverse-dns":
        return "address"
    if module_id == "network.subnet-calculator":
        return "network"
    if module_id in {"web.url-analyzer", "web.security-headers"}:
        return "url"
    if module_id == "web.tls-inspector":
        return "hostname"
    return None


class PhantomSecWindow:
    """Single-window terminal-style Phantom Sec application."""

    def __init__(self, root: typing.Any):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.store = Store()
        self.results: queue.Queue[tuple[str, typing.Any]] = queue.Queue()
        self.selected_module: Module | None = None
        self.visible_modules: list[Module] = []
        self.input_value = tk.StringVar()
        self.search_value = tk.StringVar()
        self.filter_value = tk.StringVar(value="ALL TOOLS")
        self.status_value = tk.StringVar(value="READY")
        self.current_view = "catalogue"
        self._configure_window()
        self._build_styles()
        self._build_shell()
        self._show_catalogue()
        self.root.after(120, self._poll_results)
        self.root.bind("<Control-k>", lambda _event: self.search_entry.focus_set())
        self.root.bind("<Control-K>", lambda _event: self.search_entry.focus_set())
        self.root.bind("<Escape>", lambda _event: self.back_to_catalogue())
        self.root.bind("<Return>", lambda _event: self.run_selected()
                       if self.current_view == "tool" else None)

    def _configure_window(self) -> None:
        self.root.title(f"Phantom Sec {__version__}")
        self.root.geometry("1180x760")
        self.root.minsize(900, 620)
        self.root.configure(background=BLACK)

    def _build_styles(self) -> None:
        style = self.ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except self.tk.TclError:
            pass
        style.configure(".", font=FONT, background=BLACK, foreground=WHITE)
        style.configure("TFrame", background=BLACK)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BLACK, foreground=WHITE, font=FONT)
        style.configure("Muted.TLabel", background=BLACK, foreground=GREY, font=FONT)
        style.configure("Panel.TLabel", background=PANEL, foreground=WHITE, font=FONT)
        style.configure("TButton", background="#202020", foreground=WHITE,
                        borderwidth=1, relief="flat", padding=(10, 7), font=FONT)
        style.map("TButton", background=[("active", "#303030")],
                  foreground=[("active", WHITE)])
        style.configure("TEntry", fieldbackground="#111111", foreground=WHITE,
                        insertcolor=WHITE, borderwidth=1, padding=9, font=FONT)
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=WHITE, rowheight=29, borderwidth=0, font=FONT)
        style.configure("Treeview.Heading", background="#202020", foreground=WHITE,
                        font=FONT_BOLD, relief="flat")

    def _build_shell(self) -> None:
        ttk = self.ttk
        header = ttk.Frame(self.root, padding=(22, 10, 22, 8))
        header.pack(fill="x")
        ttk.Label(header, text="PHANTOM SEC", font=("Cascadia Mono", 11, "bold"),
                  foreground=WHITE).pack(side="left")
        ttk.Label(header, text=f"v{__version__}", style="Muted.TLabel").pack(side="right")
        self.body = ttk.Frame(self.root, padding=(20, 8, 20, 8))
        self.body.pack(fill="both", expand=True)
        footer = ttk.Frame(self.root, padding=(20, 5, 20, 10))
        footer.pack(fill="x")
        ttk.Separator(footer, orient="horizontal").pack(fill="x", pady=(0, 7))
        ttk.Label(footer, textvariable=self.status_value, style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="LOCAL TOOLS  ·  READ-ONLY BY DEFAULT",
                  style="Muted.TLabel").pack(side="right")

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()

    def _show_catalogue(self) -> None:
        tk, ttk = self.tk, self.ttk
        self.current_view = "catalogue"
        self.selected_module = None
        self._clear_body()
        self.body.columnconfigure(0, weight=0, minsize=410)
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)

        catalogue = ttk.Frame(self.body)
        catalogue.grid(row=0, column=0, sticky="nsew", padx=(0, 28))
        catalogue.columnconfigure(0, weight=1)
        catalogue.rowconfigure(3, weight=1)

        ttk.Label(catalogue, text="SELECT AN OPERATION MODULE",
                  style="Muted.TLabel").grid(row=0, column=0, sticky="w", pady=(2, 10))
        search_row = ttk.Frame(catalogue)
        search_row.grid(row=1, column=0, sticky="ew", pady=(0, 7))
        search_row.columnconfigure(1, weight=1)
        ttk.Label(search_row, text="SEARCH >", style="Muted.TLabel").grid(
            row=0, column=0, padx=(0, 8))
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_value)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.configure(takefocus=True)
        self.search_value.trace_add("write", lambda *_: self._refresh_catalogue())

        filters = ttk.Frame(catalogue)
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(filters, text="★ FAVOURITES",
                   command=lambda: self._set_filter("FAVOURITES")).pack(side="left")
        ttk.Button(filters, text="RECENT",
                   command=lambda: self._set_filter("RECENT")).pack(side="left", padx=(6, 0))
        ttk.Button(filters, text="ALL",
                   command=lambda: self._set_filter("ALL TOOLS")).pack(side="left", padx=(6, 0))
        ttk.Label(filters, textvariable=self.filter_value,
                  style="Muted.TLabel").pack(side="right")

        list_frame = ttk.Frame(catalogue)
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.tool_list = tk.Listbox(
            list_frame, bg=BLACK, fg=RED, selectbackground="#292929",
            selectforeground=RED, highlightthickness=1, highlightbackground="#444444",
            highlightcolor="#777777", borderwidth=0, activestyle="none",
            font=("Cascadia Mono", 11), exportselection=False,
        )
        self.tool_list.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tool_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tool_list.configure(yscrollcommand=scroll.set)
        self.tool_list.bind("<Double-Button-1>", self._open_selected)
        self.tool_list.bind("<Return>", self._open_selected)
        self.tool_list.bind("<<ListboxSelect>>", self._catalogue_selection)
        ttk.Label(catalogue, text="DOUBLE-CLICK OR PRESS ENTER TO OPEN",
                  style="Muted.TLabel").grid(row=4, column=0, sticky="w", pady=(8, 0))

        stage = ttk.Frame(self.body)
        stage.grid(row=0, column=1, sticky="nsew")
        stage.columnconfigure(0, weight=1)
        stage.rowconfigure(0, weight=1)
        artwork = ttk.Frame(stage)
        artwork.grid(row=0, column=0, sticky="nsew")
        artwork.columnconfigure(0, weight=1)
        artwork.rowconfigure(0, weight=1)
        mark = (
            "       .--------.       \n"
            "      /  .----.  \\      \n"
            "     /  /      \\  \\     \n"
            "    |  |  ____  |  |    \n"
            "    |  | |    | |  |    \n"
            "    |  | |____| |  |    \n"
            "     \\  \\      /  /     \n"
            "      \\  '----'  /      \n"
            "       '--------'       "
        )
        ttk.Label(artwork, text=mark, font=("Cascadia Mono", 18),
                  foreground="#b8b8b8", justify="center").grid(
                      row=0, column=0, sticky="s", pady=(0, 16))
        ttk.Label(artwork, text="SECURITY  ·  PRIVACY  ·  DIAGNOSTICS",
                  style="Muted.TLabel").grid(row=1, column=0, sticky="n", pady=(0, 12))
        ttk.Label(stage, text="READY FOR LOCAL OPERATIONS",
                  style="Muted.TLabel").grid(row=1, column=0, sticky="e", pady=(8, 2))
        self._refresh_catalogue()
        self.search_entry.focus_set()

    def _set_filter(self, value: str) -> None:
        self.filter_value.set(value)
        self._refresh_catalogue()

    def _refresh_catalogue(self) -> None:
        if not hasattr(self, "tool_list") or self.current_view != "catalogue":
            return
        self.tool_list.delete(0, "end")
        modules = search_modules(self.search_value.get())
        mode = self.filter_value.get()
        if mode == "FAVOURITES":
            saved = set(self.store.favorites())
            modules = [item for item in modules if item.module_id in saved]
        elif mode == "RECENT":
            recent_ids = [row["module_id"] for row in self.store.history(100)]
            rank = {module_id: index for index, module_id in enumerate(recent_ids)}
            modules = [item for item in modules if item.module_id in rank]
            modules.sort(key=lambda item: rank[item.module_id])
        self.visible_modules = modules
        for index, module in enumerate(modules, 1):
            marker = "  ★" if self.store.is_favorite(module.module_id) else ""
            self.tool_list.insert("end", f"[{index:02d}]  {module.name}{marker}")
        if not modules:
            self.tool_list.insert("end", "No matching tools")
        self.status_value.set(f"{len(modules)} TOOLS SHOWN  ·  {mode}")

    def _catalogue_selection(self, _event: typing.Any = None) -> None:
        selection = self.tool_list.curselection()
        if selection and selection[0] < len(self.visible_modules):
            self.status_value.set(f"SELECTED  ·  {self.visible_modules[selection[0]].module_id}")

    def _open_selected(self, _event: typing.Any = None) -> None:
        selection = self.tool_list.curselection()
        if not selection or selection[0] >= len(self.visible_modules):
            return
        self.open_tool(self.visible_modules[selection[0]])

    def open_tool(self, module: Module) -> None:
        tk, ttk = self.tk, self.ttk
        self.selected_module = module
        self.current_view = "tool"
        self.input_value.set("")
        self._clear_body()
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(5, weight=1)

        top = ttk.Frame(self.body)
        top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="< BACK TO TOOL MENU",
                   command=self.back_to_catalogue).pack(side="left")
        ttk.Label(top, text="PHANTOM SEC", style="Muted.TLabel").pack(side="right")

        title = module.name.upper()
        ascii_title = f"==[ {title} ]=="
        ttk.Label(self.body, text=ascii_title,
                  font=("Cascadia Mono", 17, "bold"), foreground=WHITE).grid(
                      row=1, column=0, pady=(28, 4))
        ttk.Label(self.body, text=f"MODULE  ·  {module.module_id}",
                  style="Muted.TLabel").grid(row=2, column=0)
        ttk.Label(self.body, text=module.description, style="Muted.TLabel",
                  wraplength=850, justify="center").grid(
                      row=3, column=0, pady=(15, 20))

        input_frame = ttk.Frame(self.body)
        input_frame.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        input_frame.columnconfigure(1, weight=1)
        kind = input_kind(module.module_id)
        label = {
            "path": "FILE / FOLDER PATH",
            "domain": "DOMAIN NAME",
            "address": "IP ADDRESS",
            "network": "IP NETWORK / CIDR",
            "hostname": "HOSTNAME",
            "url": "WEBSITE URL",
        }.get(kind, "INPUT")
        ttk.Label(input_frame, text=f"{label}  >", style="Muted.TLabel").grid(
            row=0, column=0, padx=(0, 10))
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_value)
        self.input_entry.grid(row=0, column=1, sticky="ew")
        if kind is None:
            self.input_entry.configure(state="disabled")
        if kind == "path":
            ttk.Button(input_frame, text="BROWSE",
                       command=self._browse_path).grid(row=0, column=2, padx=(8, 0))

        controls = ttk.Frame(self.body)
        controls.grid(row=5, column=0, sticky="nsew")
        controls.columnconfigure(0, weight=1)
        controls.rowconfigure(2, weight=1)
        action_row = ttk.Frame(controls)
        action_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.run_button = ttk.Button(action_row, text="[ EXECUTE ]",
                                     command=self.run_selected)
        self.run_button.pack(side="left")
        self.favorite_button = ttk.Button(
            action_row, text="★ REMOVE FAVOURITE" if self.store.is_favorite(module.module_id)
            else "☆ ADD FAVOURITE", command=self._toggle_favorite)
        self.favorite_button.pack(side="left", padx=(8, 0))
        ttk.Button(action_row, text="COPY OUTPUT", command=self._copy_result).pack(
            side="left", padx=(8, 0))
        ttk.Button(action_row, text="SAVE OUTPUT", command=self._export_output).pack(
            side="left", padx=(8, 0))
        ttk.Button(action_row, text="CLEAR", command=self._clear_result).pack(
            side="left", padx=(8, 0))

        ttk.Label(controls, text="OUTPUT TERMINAL", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 6))
        output_frame = ttk.Frame(controls)
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        self.output = tk.Text(
            output_frame, wrap="word", bg=BLACK, fg=WHITE, insertbackground=WHITE,
            selectbackground="#444444", relief="flat", highlightthickness=1,
            highlightbackground="#444444", padx=12, pady=10,
            font=("Cascadia Mono", 10),
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        output_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview)
        output_scroll.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=output_scroll.set)
        self._set_output("Waiting for execution...\n")
        self.status_value.set(f"READY  ·  {module.module_id}")
        if kind:
            self.input_entry.focus_set()

    def back_to_catalogue(self) -> None:
        if self.current_view == "tool":
            self._show_catalogue()

    def _toggle_favorite(self) -> None:
        if not self.selected_module:
            return
        module_id = self.selected_module.module_id
        saved = self.store.is_favorite(module_id)
        self.store.set_favorite(module_id, not saved)
        self.favorite_button.configure(
            text="☆ ADD FAVOURITE" if saved else "★ REMOVE FAVOURITE")
        self.status_value.set("FAVOURITE REMOVED" if saved else "FAVOURITE SAVED")

    def _browse_path(self) -> None:
        from tkinter import filedialog

        if not self.selected_module:
            return
        module_id = self.selected_module.module_id
        if module_id in {"file.directory-size", "file.duplicate-finder", "system.disk"}:
            chosen = filedialog.askdirectory()
        else:
            chosen = filedialog.askopenfilename()
        if chosen:
            self.input_value.set(chosen)

    def run_selected(self) -> None:
        if not self.selected_module or self.current_view != "tool":
            return
        module = self.selected_module
        kind = input_kind(module.module_id)
        value = self.input_value.get().strip()
        if kind and not value:
            self.status_value.set(f"INPUT REQUIRED  ·  {kind.upper()}")
            self.input_entry.focus_set()
            return
        kwargs = {kind: value} if kind else {}
        self.run_button.configure(state="disabled")
        self.status_value.set(f"RUNNING  ·  {module.module_id}")
        self._set_output(f"> EXECUTING {module.name.upper()}...\n")

        def worker() -> None:
            try:
                result = run_module(module.module_id, **kwargs)
                self.store.record_run(module.module_id, result)
                self.results.put(("success", result))
            except Exception as exc:
                self.results.put(("error", f"{type(exc).__name__}: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_results(self) -> None:
        try:
            while True:
                kind, payload = self.results.get_nowait()
                if self.current_view == "tool" and self.selected_module:
                    self.run_button.configure(state="normal")
                    if kind == "success":
                        self._set_output(json.dumps(
                            payload, indent=2, ensure_ascii=False, default=str))
                        self.status_value.set("EXECUTION COMPLETE")
                    else:
                        self._set_output(f"TOOL ERROR\n{payload}")
                        self.status_value.set("EXECUTION FAILED")
                elif kind == "success":
                    self.status_value.set("TOOL COMPLETED")
        except queue.Empty:
            pass
        self.root.after(120, self._poll_results)

    def _set_output(self, value: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", value)
        self.output.configure(state="disabled")

    def _clear_result(self) -> None:
        self._set_output("Waiting for execution...\n")
        self.status_value.set("OUTPUT CLEARED")

    def _copy_result(self) -> None:
        value = self.output.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.status_value.set("OUTPUT COPIED")

    def _export_output(self) -> None:
        from tkinter import filedialog

        if not hasattr(self, "output"):
            return
        destination = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")],
            title="Save Phantom Sec output",
        )
        if destination:
            from pathlib import Path
            Path(destination).write_text(
                self.output.get("1.0", "end-1c"), encoding="utf-8")
            self.status_value.set("OUTPUT SAVED")

