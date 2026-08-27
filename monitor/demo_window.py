"""
SmartFix AI — Demo Mode Selection Window
A beautiful window for judges to select and trigger demo scenarios.
"""
import tkinter as tk
from typing import Callable, List, Dict, Any

COLORS = {
    "bg_dark":       "#090A0F",
    "bg_card":       "#12141D",
    "bg_header":     "#090A0F",
    "accent":        "#5A67D8",
    "accent_green":  "#38A169",
    "accent_red":    "#FF3A3A",
    "accent_orange": "#FF8C00",
    "text_primary":  "#F7FAFC",
    "text_secondary":"#A0AEC0",
    "border":        "#2D313F",
    "hover":         "#1A1D27",
    "CRITICAL": "#FF3A3A",
    "HIGH":     "#FF8C00",
    "MEDIUM":   "#FFD700",
    "LOW":      "#4F8EF7",
}

SEVERITY_ICONS = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}


class DemoWindow:
    """
    Judge-facing demo launcher window.
    Shows all available demo scenarios in a list with a 'Trigger Demo' button.
    """

    def __init__(self, scenarios: List[Any], on_run: Callable[[str], None], on_close: Callable = None):
        self.scenarios = scenarios
        self.on_run = on_run
        self.on_close = on_close
        self._root: tk.Tk = None

    def show(self):
        self._root = root = tk.Tk()
        root.title("SmartFix AI — Judge Demo Mode")
        root.configure(bg=COLORS["bg_dark"])
        root.resizable(False, False)
        root.attributes("-topmost", True)

        self._build_ui(root)

        root.update_idletasks()
        w, h = root.winfo_width(), root.winfo_height()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")
        root.mainloop()

    def _build_ui(self, root: tk.Tk):
        
        hdr = tk.Frame(root, bg="#161B22", padx=24, pady=14)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🎭  SmartFix AI — Demo Mode",
                 bg="#161B22", fg=COLORS["text_primary"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")

        tk.Button(hdr, text="✕", command=self._close,
                  bg="#161B22", fg=COLORS["text_secondary"],
                  relief="flat", cursor="hand2", font=("Segoe UI", 11),
                  activebackground=COLORS["accent_red"], bd=0, padx=6).pack(side="right")

        
        sub = tk.Frame(root, bg=COLORS["bg_dark"], padx=24, pady=8)
        sub.pack(fill="x")
        tk.Label(sub, text="Select a scenario below and click  Trigger Demo  to simulate an error and watch SmartFix fix it in real time.",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=("Segoe UI", 9), wraplength=560, justify="left").pack(anchor="w")

        tk.Frame(root, height=1, bg=COLORS["border"]).pack(fill="x", padx=0)

        
        list_frame = tk.Frame(root, bg=COLORS["bg_dark"], padx=20, pady=16)
        list_frame.pack(fill="both", expand=True)

        self._selected_var = tk.StringVar(value=self.scenarios[0].error_id if self.scenarios else "")

        for sc in self.scenarios:
            self._make_scenario_row(list_frame, sc)

        tk.Frame(root, height=1, bg=COLORS["border"]).pack(fill="x")

        
        bar = tk.Frame(root, bg=COLORS["bg_card"], padx=24, pady=14)
        bar.pack(fill="x")

        status_label = tk.Label(bar, text="Select a scenario above, then click Trigger Demo.",
                                bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                                font=("Segoe UI", 9))
        status_label.pack(side="left")

        self._status_label = status_label

        btn = tk.Button(bar, text="  ▶  Trigger Demo  ",
                        command=self._trigger,
                        bg=COLORS["accent_green"], fg="white",
                        font=("Segoe UI", 10, "bold"),
                        relief="flat", cursor="hand2",
                        activebackground="#00B85C",
                        padx=20, pady=8)
        btn.pack(side="right")
        btn.bind("<Enter>", lambda e: btn.config(bg="#00B85C"))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["accent_green"]))

    def _make_scenario_row(self, parent, sc):
        row_bg = COLORS["bg_card"]

        row = tk.Frame(parent, bg=row_bg, padx=16, pady=12,
                       highlightbackground=COLORS["border"], highlightthickness=1,
                       cursor="hand2")
        row.pack(fill="x", pady=4)

        
        rb = tk.Radiobutton(row, variable=self._selected_var, value=sc.error_id,
                            bg=row_bg, activebackground=row_bg,
                            selectcolor=COLORS["accent"])
        rb.pack(side="left")

        
        idx = self.scenarios.index(sc) + 1
        num_badge = tk.Label(row, text=f" {idx} ",
                             bg=COLORS["accent"], fg="white",
                             font=("Segoe UI", 8, "bold"), padx=6, pady=2)
        num_badge.pack(side="left", padx=(0, 10))

        
        col = tk.Frame(row, bg=row_bg)
        col.pack(side="left", fill="x", expand=True)

        tk.Label(col, text=sc.name, bg=row_bg, fg=COLORS["text_primary"],
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")

        tk.Label(col, text=sc.description, bg=row_bg, fg=COLORS["text_secondary"],
                 font=("Segoe UI", 8), anchor="w", wraplength=420, justify="left").pack(anchor="w")

        
        for widget in [row, col]:
            widget.bind("<Button-1>", lambda e, eid=sc.error_id: self._selected_var.set(eid))

        
        def on_enter(e, f=row):
            f.config(bg=COLORS["hover"])
        def on_leave(e, f=row):
            f.config(bg=row_bg)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)

    def _trigger(self):
        selected = self._selected_var.get()
        if not selected:
            self._status_label.config(text="Please select a scenario first.", fg=COLORS["accent_red"])
            return

        sc = next((s for s in self.scenarios if s.error_id == selected), None)
        if not sc:
            return

        self._status_label.config(
            text=f"⚙ Running demo: {sc.name}…  Watch for the alert popup!",
            fg=COLORS["accent_green"]
        )
        self._root.update()

        
        self._root.after(800, lambda: self._run_and_close(selected))

    def _run_and_close(self, scenario_id: str):
        self.on_run(scenario_id)
        self._close()

    def _close(self):
        try:
            self._root.destroy()
        except Exception:
            pass
        if self.on_close:
            self.on_close()
