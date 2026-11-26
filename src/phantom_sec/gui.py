"""Native desktop interface for Phantom Sec.

The interface uses Python's standard-library Tk toolkit and performs tool runs
in a worker thread so the window stays responsive.
"""

from __future__ import annotations

import json
import queue
import threading
from typing import Any

from phantom_sec import __version__
from phantom_sec.local_history import Store
from phantom_sec.modules import Module, get_modules, run_module


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


def dashboard_summary(store: Store) -> dict[str, Any]:
    """Return small, local-only dashboard statistics."""
    modules = get_modules()
    recent = store.history(1)
    return {
        "tool_count": len(modules),
        "category_count": len({module.category for module in modules}),
        "recent_run": recent[0] if recent else None,
        "favorite_count": len(store.favorites()),
    }


def input_kind(module_id: str) -> str | None:
    """Return the single input field needed by a built-in tool, if any."""
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
    """Build and run the Phantom Sec desktop window."""

    def __init__(self, root: Any):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.store = Store()
        self.results: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.selected_module: Module | None = None
        self.input_value = tk.StringVar()
        self.search_value = tk.StringVar()
        self.category_value = tk.StringVar(value="All tools")
        self.status_value = tk.StringVar(value="Ready")
        self._configure_window()
        self._build_styles()
        self._build_layout()
        self._refresh_catalogue()
        self._refresh_dashboard()
        self.root.after(120, self._poll_results)
        self.root.bind("<Control-k>", lambda _event: self.search_entry.focus_set())
        self.root.bind("<Control-K>", lambda _event: self.search_entry.focus_set())
        self.input_entry.bind("<Return>", lambda _event: self.run_selected())

    def _configure_window(self) -> None:
        self.root.title(f"Phantom Sec {__version__}")
        self.root.geometry("1180x760")
        self.root.minsize(900, 620)
        self.root.configure(background="#171b18")

    def _build_styles(self) -> None:
        style = self.ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except self.tk.TclError:
            pass
        style.configure(".", font=("Segoe UI", 10), background="#202722",
                        foreground="#e9e6dc")
        style.configure("TFrame", background="#171b18")
        style.configure("Panel.TFrame", background="#202722")
        style.configure("TLabel", background="#171b18", foreground="#e9e6dc")
        style.configure("Muted.TLabel", background="#171b18", foreground="#a5aa9b")
        style.configure("Panel.TLabel", background="#202722", foreground="#e9e6dc")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"),
                        background="#171b18", foreground="#f2efe5")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10),
                        background="#171b18", foreground="#a5aa9b")
        style.configure("Section.TLabel", font=("Segoe UI", 13, "bold"),
                        background="#202722", foreground="#f2efe5")
        style.configure("Accent.TButton", background="#a8c6a0", foreground="#f2efe5",
                        padding=(16, 9), borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#bdd4b4"), ("disabled", "#49554a")])
        style.configure("TButton", padding=(10, 7), background="#303a32",
                        foreground="#e9e6dc", borderwidth=0)
        style.map("TButton", background=[("active", "#3c493e")])
        style.configure("TEntry", fieldbackground="#29322b", foreground="#f2efe5",
                        insertcolor="#f2efe5", padding=9, borderwidth=0)
        style.configure("TCombobox", fieldbackground="#29322b", foreground="#f2efe5",
                        padding=7)
        style.configure("Treeview", background="#202722", fieldbackground="#202722",
                        foreground="#e9e6dc", rowheight=31, borderwidth=0)
        style.configure("Treeview.Heading", background="#303a32", foreground="#d8c8a8",
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#465b49")],
                  foreground=[("selected", "#f2efe5")])
        style.configure("TNotebook", background="#171b18", borderwidth=0)
        style.configure("TNotebook.Tab", background="#29322b", foreground="#d8c8a8",
                        padding=(14, 9))
        style.map("TNotebook.Tab", background=[("selected", "#202722")],
                  foreground=[("selected", "#f2efe5")])

    def _build_layout(self) -> None:
        ttk = self.ttk
        header = ttk.Frame(self.root, padding=(24, 18, 24, 12))
        header.pack(fill="x")
        brand = ttk.Frame(header)
        brand.pack(side="left")
        ttk.Label(brand, text="PHANTOM SEC", style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand, text="LOCAL SECURITY WORKBENCH  •  QUIETLY CAPABLE  •  READ-ONLY BY DEFAULT",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
        ttk.Label(header, text=f"v{__version__}", style="Muted.TLabel").pack(side="right", anchor="n")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.dashboard_tab = ttk.Frame(self.notebook, padding=24)
        self.tools_tab = ttk.Frame(self.notebook, padding=16)
        self.history_tab = ttk.Frame(self.notebook, padding=16)
        self.about_tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.tools_tab, text="Tool library")
        self.notebook.add(self.history_tab, text="Run history")
        self.notebook.add(self.about_tab, text="About")
        self._build_dashboard_tab()
        self._build_tools_tab()
        self._build_history_tab()
        self._build_about_tab()

        footer = ttk.Frame(self.root, padding=(22, 5, 22, 12))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status_value, style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="Use only on systems you own or are authorized to assess.",
                  style="Muted.TLabel").pack(side="right")

    def _build_dashboard_tab(self) -> None:
        ttk = self.ttk
        panel = ttk.Frame(self.dashboard_tab, style="Panel.TFrame", padding=24)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Welcome to Phantom Sec", style="Section.TLabel").pack(
            anchor="w")
        ttk.Label(
            panel,
            text="A quick snapshot of your local toolkit and recent activity.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(5, 22))

        stats = ttk.Frame(panel, style="Panel.TFrame")
        stats.pack(fill="x", pady=(0, 20))
        self.dashboard_tools = ttk.Label(stats, text="Built-in tools: —", style="Section.TLabel")
        self.dashboard_tools.pack(anchor="w", pady=5)
        self.dashboard_categories = ttk.Label(
            stats, text="Tool categories: —", style="Section.TLabel")
        self.dashboard_categories.pack(anchor="w", pady=5)
        self.dashboard_recent = ttk.Label(
            stats, text="Latest run: No runs recorded yet", style="Panel.TLabel")
        self.dashboard_recent.pack(anchor="w", pady=(12, 5))
        self.dashboard_favorites = ttk.Label(
            stats, text="Favourite tools: 0", style="Panel.TLabel")
        self.dashboard_favorites.pack(anchor="w", pady=5)

        actions = ttk.Frame(panel, style="Panel.TFrame")
        actions.pack(anchor="w", pady=(12, 0))
        ttk.Button(actions, text="Open tool library", style="Accent.TButton",
                   command=lambda: self.notebook.select(self.tools_tab)).pack(side="left")
        ttk.Button(actions, text="Refresh dashboard",
                   command=self._refresh_dashboard).pack(side="left", padx=(10, 0))

    def _refresh_dashboard(self) -> None:
        if not hasattr(self, "dashboard_tools"):
            return
        summary = dashboard_summary(self.store)
        self.dashboard_tools.configure(
            text=f"Built-in tools: {summary['tool_count']}")
        self.dashboard_categories.configure(
            text=f"Tool categories: {summary['category_count']}")
        self.dashboard_favorites.configure(
            text=f"Favourite tools: {summary['favorite_count']}")
        recent = summary["recent_run"]
        if recent:
            stamp = recent["created_at"].replace("T", " ").replace("+00:00", " UTC")
            self.dashboard_recent.configure(
                text=f"Latest run: {recent['module_id']}  ·  {stamp}")
        else:
            self.dashboard_recent.configure(text="Latest run: No runs recorded yet")

    def _build_tools_tab(self) -> None:
        tk, ttk = self.tk, self.ttk
        self.tools_tab.columnconfigure(0, weight=0, minsize=330)
        self.tools_tab.columnconfigure(1, weight=1)
        self.tools_tab.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.tools_tab, style="Panel.TFrame", padding=14)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar.rowconfigure(3, weight=1)
        ttk.Label(sidebar, text="Find a tool", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 9))
        self.search_entry = ttk.Entry(sidebar, textvariable=self.search_value)
        self.search_entry.grid(row=1, column=0, sticky="ew", pady=(0, 9))
        self.search_entry.configure(takefocus=True)
        self.search_value.trace_add("write", lambda *_: self._refresh_catalogue())
        categories = ["All tools", "★ Favourites", *sorted({item.category for item in get_modules()})]
        self.category_box = ttk.Combobox(
            sidebar, textvariable=self.category_value, values=categories,
            state="readonly",
        )
        self.category_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.category_box.bind("<<ComboboxSelected>>", lambda _event: self._refresh_catalogue())
        self.tool_list = tk.Listbox(
            sidebar, bg="#202722", fg="#e9e6dc", selectbackground="#465b49",
            selectforeground="#f2efe5", highlightthickness=0, borderwidth=0,
            activestyle="none", font=("Segoe UI", 10), exportselection=False,
        )
        self.tool_list.grid(row=3, column=0, sticky="nsew")
        list_scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.tool_list.yview)
        list_scroll.grid(row=3, column=1, sticky="ns")
        self.tool_list.configure(yscrollcommand=list_scroll.set)
        self.tool_list.bind("<<ListboxSelect>>", self._on_tool_selected)
        self.tool_list.bind("<Double-Button-1>", lambda _event: self.run_selected())
        self.visible_modules: list[Module] = []
        ttk.Label(sidebar, text="Tip: press Ctrl+K to search",
                  style="Muted.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 0))

        detail = ttk.Frame(self.tools_tab, style="Panel.TFrame", padding=20)
        detail.grid(row=0, column=1, sticky="nsew")
        detail.columnconfigure(0, weight=1)
        detail.rowconfigure(5, weight=1)
        self.detail_category = ttk.Label(detail, text="TOOL DETAILS", style="Muted.TLabel")
        self.detail_category.grid(row=0, column=0, sticky="w")
        self.detail_title = ttk.Label(detail, text="Choose a tool", style="Section.TLabel")
        self.detail_title.grid(row=1, column=0, sticky="w", pady=(7, 3))
        self.detail_id = ttk.Label(detail, text="Select a tool from the library",
                                   style="Muted.TLabel")
        self.detail_id.grid(row=2, column=0, sticky="w")
        self.detail_description = ttk.Label(
            detail, text="Search by name, tool ID, or description. Select a result to see details.",
            style="Panel.TLabel", wraplength=600, justify="left",
        )
        self.detail_description.grid(row=3, column=0, sticky="w", pady=(15, 14))

        input_row = ttk.Frame(detail, style="Panel.TFrame")
        input_row.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        input_row.columnconfigure(1, weight=1)
        self.input_label = ttk.Label(input_row, text="Input", style="Panel.TLabel")
        self.input_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.input_entry = ttk.Entry(input_row, textvariable=self.input_value)
        self.input_entry.grid(row=0, column=1, sticky="ew")
        self.browse_button = ttk.Button(input_row, text="Browse…", command=self._browse_path)
        self.browse_button.grid(row=0, column=2, padx=(8, 0))
        self.input_row = input_row

        actions = ttk.Frame(detail, style="Panel.TFrame")
        actions.grid(row=5, column=0, sticky="nsew")
        actions.rowconfigure(2, weight=1)
        actions.columnconfigure(0, weight=1)
        top_actions = ttk.Frame(actions, style="Panel.TFrame")
        top_actions.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.run_button = ttk.Button(top_actions, text="Run tool", style="Accent.TButton",
                                     command=self.run_selected, state="disabled")
        self.run_button.pack(side="left")
        self.favorite_button = ttk.Button(
            top_actions, text="☆ Add favourite", command=self._toggle_favorite, state="disabled")
        self.favorite_button.pack(side="left", padx=(8, 0))
        ttk.Button(top_actions, text="Copy result", command=self._copy_result).pack(
            side="left", padx=(8, 0))
        ttk.Button(top_actions, text="Export JSON", command=self._export_output).pack(
            side="left", padx=(8, 0))
        ttk.Button(top_actions, text="Clear", command=self._clear_result).pack(
            side="left", padx=(8, 0))
        ttk.Label(actions, text="OUTPUT", style="Muted.TLabel").grid(
            row=1, column=0, sticky="nw", pady=(3, 5))
        output_frame = ttk.Frame(actions, style="Panel.TFrame")
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        self.output = tk.Text(
            output_frame, height=12, wrap="word", bg="#171b18", fg="#e9e6dc",
            insertbackground="#f2efe5", selectbackground="#465b49", relief="flat",
            padx=12, pady=10, font=("Cascadia Code", 10),
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scroll.set)
        self.output.insert("1.0", "Results will appear here after you run a tool.")
        self.output.configure(state="disabled")

    def _build_history_tab(self) -> None:
        ttk = self.ttk
        self.history_tab.columnconfigure(0, weight=1)
        self.history_tab.rowconfigure(1, weight=1)
        heading = ttk.Frame(self.history_tab)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(heading, text="Recent activity", style="Section.TLabel").pack(side="left")
        ttk.Button(heading, text="Refresh", command=self._refresh_history).pack(side="right")
        self.history_tree = ttk.Treeview(
            self.history_tab, columns=("time", "tool"), show="headings", height=16,
        )
        self.history_tree.heading("time", text="Date and time")
        self.history_tree.heading("tool", text="Tool")
        self.history_tree.column("time", width=260, anchor="w")
        self.history_tree.column("tool", width=420, anchor="w")
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        self._refresh_history()

    def _build_about_tab(self) -> None:
        ttk = self.ttk
        panel = ttk.Frame(self.about_tab, style="Panel.TFrame", padding=24)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Phantom Sec", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text=f"Version {__version__}", style="Muted.TLabel").pack(
            anchor="w", pady=(4, 16))
        copy = (
            "A local-first toolkit for defensive security, responsible OSINT, "
            "network diagnostics, and system administration.\n\n"
            "Safety by design\n"
            "• Built-in tools are designed to inspect, not alter, your system.\n"
            "• No third-party module code is executed.\n"
            "• Run tools only on devices and networks you own or are authorized to assess.\n\n"
            "Privacy\n"
            "• Run history is stored locally in your user profile.\n"
            "• Reports may contain device details. Review them before sharing.\n"
            "• This preview is not a complete security audit or a guarantee of security."
        )
        ttk.Label(panel, text=copy, style="Panel.TLabel", justify="left",
                  wraplength=800).pack(anchor="w")

    def _refresh_catalogue(self) -> None:
        self.tool_list.delete(0, "end")
        self.selected_module = None
        self.run_button.configure(state="disabled")
        self.favorite_button.configure(state="disabled", text="☆ Add favourite")
        self.detail_category.configure(text="TOOL DETAILS")
        self.detail_title.configure(text="Choose a tool")
        self.detail_id.configure(text="Select a tool from the library")
        self.detail_description.configure(
            text="Search by name, tool ID, or description. Select a result to see details."
        )
        self.input_value.set("")
        self.input_label.configure(text="No input required")
        self.input_entry.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        selected_category = self.category_value.get()
        self.visible_modules = search_modules(
            self.search_value.get(),
            "All tools" if selected_category == "★ Favourites" else selected_category,
        )
        if selected_category == "★ Favourites":
            saved = set(self.store.favorites())
            self.visible_modules = [item for item in self.visible_modules if item.module_id in saved]
        for module in self.visible_modules:
            self.tool_list.insert("end", f"{module.name}   ·   {module.module_id}")
        if not self.visible_modules:
            self.tool_list.insert("end", "No matching tools")
        self.status_value.set(f"{len(self.visible_modules)} tools shown")

    def _on_tool_selected(self, _event: Any = None) -> None:
        selection = self.tool_list.curselection()
        if not selection or selection[0] >= len(self.visible_modules):
            return
        self.selected_module = self.visible_modules[selection[0]]
        module = self.selected_module
        self.detail_category.configure(text=module.category.upper())
        self.detail_title.configure(text=module.name)
        self.detail_id.configure(text=module.module_id)
        self.detail_description.configure(text=module.description)
        kind = input_kind(module.module_id)
        self.input_value.set("")
        if kind:
            self.input_label.configure(text={
                "path": "File / folder path",
                "domain": "Hostname",
                "address": "IP address",
                "network": "IP network (CIDR)",
                "hostname": "Hostname",
                "url": "HTTP or HTTPS URL",
                "domain": "Public domain name",
            }[kind])
            self.input_entry.configure(state="normal")
            self.browse_button.configure(state="normal" if kind == "path" else "disabled")
        else:
            self.input_label.configure(text="No input required")
            self.input_entry.configure(state="disabled")
            self.browse_button.configure(state="disabled")
        self.run_button.configure(state="normal")
        self._update_favorite_button()
        self.status_value.set(f"Selected {module.module_id}")

    def _update_favorite_button(self) -> None:
        if not self.selected_module:
            self.favorite_button.configure(state="disabled", text="☆ Add favourite")
            return
        saved = self.store.is_favorite(self.selected_module.module_id)
        self.favorite_button.configure(
            state="normal", text="★ Remove favourite" if saved else "☆ Add favourite")

    def _toggle_favorite(self) -> None:
        if not self.selected_module:
            return
        module_id = self.selected_module.module_id
        self.store.set_favorite(module_id, not self.store.is_favorite(module_id))
        self._update_favorite_button()
        self._refresh_dashboard()
        if self.category_value.get() == "★ Favourites":
            self._refresh_catalogue()
        self.status_value.set(
            "Favourite updated" if self.store.is_favorite(module_id)
            else "Favourite removed")

    def _browse_path(self) -> None:
        from tkinter import filedialog

        if not self.selected_module:
            return
        if self.selected_module.module_id in {"file.directory-size", "file.duplicate-finder", "system.disk"}:
            chosen = filedialog.askdirectory()
        else:
            chosen = filedialog.askopenfilename()
        if chosen:
            self.input_value.set(chosen)

    def run_selected(self) -> None:
        if not self.selected_module:
            return
        module = self.selected_module
        kind = input_kind(module.module_id)
        value = self.input_value.get().strip()
        if kind and not value:
            self.status_value.set(f"Enter a {kind} before running this tool.")
            self.input_entry.focus_set()
            return
        kwargs = {kind: value} if kind else {}
        self.run_button.configure(state="disabled")
        self.status_value.set(f"Running {module.module_id}…")
        self._set_output(f"Running {module.name}…")

        def worker() -> None:
            try:
                result = run_module(module.module_id, **kwargs)
                self.store.record_run(module.module_id, result)
                self.results.put(("success", result))
            except Exception as exc:  # Keep unexpected tool errors inside the app.
                self.results.put(("error", f"{type(exc).__name__}: {exc}"))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_results(self) -> None:
        try:
            while True:
                kind, payload = self.results.get_nowait()
                self.run_button.configure(state="normal" if self.selected_module else "disabled")
                if kind == "success":
                    self._set_output(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
                    self.status_value.set("Tool completed successfully")
                    self._refresh_history()
                    self._refresh_dashboard()
                else:
                    self._set_output(f"Tool could not finish:\n{payload}")
                    self.status_value.set("Tool returned an error")
        except queue.Empty:
            pass
        self.root.after(120, self._poll_results)

    def _set_output(self, value: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", value)
        self.output.configure(state="disabled")

    def _clear_result(self) -> None:
        self._set_output("Results will appear here after you run a tool.")
        self.status_value.set("Output cleared")

    def _copy_result(self) -> None:
        value = self.output.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.status_value.set("Output copied to clipboard")

    def _refresh_history(self) -> None:
        if not hasattr(self, "history_tree"):
            return
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for row in self.store.history(100):
            timestamp = row["created_at"].replace("T", " ").replace("+00:00", " UTC")
            self.history_tree.insert("", "end", values=(timestamp, row["module_id"]))


    def _export_output(self) -> None:
        from tkinter import filedialog, messagebox

        raw = self.output.get("1.0", "end-1c")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            messagebox.showinfo("Nothing to export", "Run a tool first to create JSON output.")
            return
        destination = filedialog.asksaveasfilename(
            title="Export tool result",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="phantom-sec-result.json",
        )
        if not destination:
            return
        try:
            with open(destination, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2, ensure_ascii=False, default=str)
                stream.write("\n")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        self.status_value.set(f"JSON exported to {destination}")


def launch_gui() -> int:
    """Start the native desktop application."""
    try:
        import tkinter as tk
    except ImportError as exc:
        raise RuntimeError(
            "The desktop interface needs Tk support. Install your Python distribution's Tk package."
        ) from exc
    try:
        root = tk.Tk()
        PhantomSecWindow(root)
        root.mainloop()
    except tk.TclError as exc:
        raise RuntimeError(
            "The desktop window could not start. Check that a graphical desktop session is available."
        ) from exc
    return 0

