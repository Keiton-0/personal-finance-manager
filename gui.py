"""
Personal Finance Manager – GUI
Requires: Python 3.9+, tkinter (stdlib)
Run:  python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar

from finance_manager import (
    FinanceManager,
    INCOME_CATEGORIES,
    EXPENSE_CATEGORIES,
    ALL_CATEGORIES,
)

# ── palette ───────────────────────────────────────────────────────────────────

BG        = "#0f0f0f"
SURFACE   = "#1a1a1a"
SURFACE2  = "#252525"
BORDER    = "#2e2e2e"
TEXT      = "#f0f0f0"
TEXT_SEC  = "#888888"
GREEN     = "#22c55e"
GREEN_DIM = "#15432e"
RED       = "#ef4444"
RED_DIM   = "#4a1414"
ACCENT    = "#6366f1"
FONT      = ("Segoe UI", 10)
FONT_B    = ("Segoe UI", 10, "bold")
FONT_LG   = ("Segoe UI", 22, "bold")
FONT_SM   = ("Segoe UI", 9)

CAT_COLORS = {
    "food": "#ef4444", "transport": "#3b82f6", "housing": "#22c55e",
    "health": "#ec4899", "education": "#8b5cf6", "entertainment": "#f59e0b",
    "clothing": "#f97316", "utilities": "#84cc16", "travel": "#14b8a6",
    "other_ex": "#6b7280", "salary": "#22c55e", "freelance": "#3b82f6",
    "investment": "#8b5cf6", "gift": "#ec4899", "other_in": "#6b7280",
}


def hex_lighten(hex_color, alpha=0.15):
    """Return a darker blended bg for a category pill."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    br, bg_, bb = int(BG.lstrip("#")[0:2], 16), int(BG.lstrip("#")[2:4], 16), int(BG.lstrip("#")[4:6], 16)
    nr = int(r * alpha + br * (1 - alpha))
    ng = int(g * alpha + bg_ * (1 - alpha))
    nb = int(b * alpha + bb * (1 - alpha))
    return f"#{nr:02x}{ng:02x}{nb:02x}"


# ── helpers ───────────────────────────────────────────────────────────────────

def styled_frame(parent, bg=SURFACE, **kw):
    return tk.Frame(parent, bg=bg, **kw)


def label(parent, text, font=FONT, fg=TEXT, bg=SURFACE, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)


def separator(parent, bg=BORDER, height=1):
    return tk.Frame(parent, bg=bg, height=height)


# ── main window ───────────────────────────────────────────────────────────────

class FinanceGUI:
    def __init__(self):
        self.fm = FinanceManager()
        self.view_month = datetime.today().month
        self.view_year  = datetime.today().year

        self._build_root()   # tk.Tk() must exist before any StringVar

        self.selected_type = tk.StringVar(value="expense")
        self.selected_cat  = tk.StringVar(value="")

        self._build_sidebar()
        self._build_main()
        self._show_panel("add")
        self._refresh_header()

    # ── root ──────────────────────────────────────────────────────────────────

    def _build_root(self):
        self.root = tk.Tk()
        self.root.title("Finance Manager")
        self.root.geometry("980x680")
        self.root.minsize(820, 580)
        self.root.configure(bg=BG)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    # ── sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = styled_frame(self.root, bg=SURFACE, width=200)
        sb.grid(row=0, column=0, sticky="ns")
        sb.grid_propagate(False)
        sb.rowconfigure(10, weight=1)

        label(sb, "💰 Finance", font=("Segoe UI", 13, "bold"), bg=SURFACE, fg=TEXT).pack(
            pady=(24, 28), padx=20, anchor="w"
        )

        self._nav_buttons = {}
        nav_items = [
            ("add",          "➕  Shto transaksion"),
            ("transactions", "📋  Transaksionet"),
            ("stats",        "📊  Statistika"),
        ]
        for key, title in nav_items:
            btn = tk.Button(
                sb, text=title, font=FONT, anchor="w",
                bg=SURFACE, fg=TEXT_SEC, relief="flat",
                padx=20, pady=10, cursor="hand2",
                command=lambda k=key: self._show_panel(k),
            )
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        separator(sb, bg=BORDER).pack(fill="x", padx=16, pady=12)

        # balance summary in sidebar
        self._sb_balance_var = tk.StringVar()
        self._sb_income_var  = tk.StringVar()
        self._sb_expense_var = tk.StringVar()

        for var, lbl, color in [
            (self._sb_balance_var, "Bilanci", TEXT),
            (self._sb_income_var,  "Të ardhura", GREEN),
            (self._sb_expense_var, "Shpenzime", RED),
        ]:
            row = styled_frame(sb, bg=SURFACE)
            row.pack(fill="x", padx=16, pady=3)
            label(row, lbl, font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(anchor="w")
            label(row, "", font=FONT_B, fg=color, bg=SURFACE, textvariable=var).pack(anchor="w")

    # ── main area ─────────────────────────────────────────────────────────────

    def _build_main(self):
        self._main = styled_frame(self.root, bg=BG)
        self._main.grid(row=0, column=1, sticky="nsew", padx=0)
        self._main.columnconfigure(0, weight=1)
        self._main.rowconfigure(0, weight=1)

        self._panels = {}
        self._panels["add"]          = self._build_add_panel(self._main)
        self._panels["transactions"] = self._build_tx_panel(self._main)
        self._panels["stats"]        = self._build_stats_panel(self._main)

        for p in self._panels.values():
            p.grid(row=0, column=0, sticky="nsew")

    # ── panel: add ────────────────────────────────────────────────────────────

    def _build_add_panel(self, parent):
        frame = styled_frame(parent, bg=BG)
        frame.columnconfigure(0, weight=1)

        # header
        label(frame, "Shto transaksion", font=("Segoe UI", 14, "bold"), bg=BG).pack(
            anchor="w", padx=28, pady=(24, 4)
        )
        label(frame, "Regjistro të ardhura ose shpenzime", font=FONT_SM, fg=TEXT_SEC, bg=BG).pack(
            anchor="w", padx=28, pady=(0, 16)
        )

        card = styled_frame(frame, bg=SURFACE)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        # type toggle
        tog = styled_frame(card, bg=SURFACE2)
        tog.pack(fill="x", padx=20, pady=(20, 16))

        self._type_btns = {}
        for val, lbl in [("income", "↑ Të ardhura"), ("expense", "↓ Shpenzim")]:
            b = tk.Button(
                tog, text=lbl, font=FONT_B, relief="flat", cursor="hand2",
                pady=8, padx=0,
                command=lambda v=val: self._set_type(v),
            )
            b.pack(side="left", fill="x", expand=True)
            self._type_btns[val] = b

        self._update_type_toggle()

        # category grid label
        label(card, "Kategoria", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=20, pady=(4, 6))
        self._cat_frame = styled_frame(card, bg=SURFACE)
        self._cat_frame.pack(fill="x", padx=20)
        self._render_cat_grid()

        # amount + date row
        fields = styled_frame(card, bg=SURFACE)
        fields.pack(fill="x", padx=20, pady=(16, 0))
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)

        label(fields, "Shuma ($)", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._amount_var = tk.StringVar()
        amt_entry = tk.Entry(
            fields, textvariable=self._amount_var, font=("Segoe UI", 14),
            bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat",
            bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        amt_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=8)
        amt_entry.bind("<Return>", lambda e: self._submit())

        label(fields, "Data", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self._date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = tk.Entry(
            fields, textvariable=self._date_var, font=FONT,
            bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat",
            bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        date_entry.grid(row=1, column=1, sticky="ew", ipady=8)

        # description
        label(card, "Përshkrim (opsional)", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(
            anchor="w", padx=20, pady=(12, 4)
        )
        self._desc_var = tk.StringVar()
        desc_entry = tk.Entry(
            card, textvariable=self._desc_var, font=FONT,
            bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat",
            bd=0, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        desc_entry.pack(fill="x", padx=20, ipady=8)
        desc_entry.bind("<Return>", lambda e: self._submit())

        # submit
        self._submit_btn = tk.Button(
            card, text="+ Shto transaksion", font=FONT_B,
            relief="flat", cursor="hand2", pady=12,
            command=self._submit,
        )
        self._submit_btn.pack(fill="x", padx=20, pady=(16, 20))
        self._update_submit_btn()

        return frame

    def _set_type(self, val):
        self.selected_type.set(val)
        self.selected_cat.set("")
        self._update_type_toggle()
        self._render_cat_grid()
        self._update_submit_btn()

    def _update_type_toggle(self):
        t = self.selected_type.get()
        self._type_btns["income"].config(
            bg=GREEN_DIM if t == "income" else SURFACE2,
            fg=GREEN     if t == "income" else TEXT_SEC,
        )
        self._type_btns["expense"].config(
            bg=RED_DIM  if t == "expense" else SURFACE2,
            fg=RED      if t == "expense" else TEXT_SEC,
        )

    def _render_cat_grid(self):
        for w in self._cat_frame.winfo_children():
            w.destroy()

        cats = INCOME_CATEGORIES if self.selected_type.get() == "income" else EXPENSE_CATEGORIES
        cols = 5
        for i, (cid, meta) in enumerate(cats.items()):
            col_color = CAT_COLORS.get(cid, "#888888")
            is_sel    = self.selected_cat.get() == cid
            bg        = hex_lighten(col_color, 0.3) if is_sel else SURFACE2
            fg        = col_color if is_sel else TEXT_SEC

            btn = tk.Button(
                self._cat_frame,
                text=f"{meta['icon']}\n{meta['name']}",
                font=FONT_SM, relief="flat", cursor="hand2",
                bg=bg, fg=fg,
                width=9, pady=8,
                command=lambda c=cid: self._select_cat(c),
            )
            btn.grid(row=i // cols, column=i % cols, padx=3, pady=3, sticky="ew")

        for c in range(cols):
            self._cat_frame.columnconfigure(c, weight=1)

    def _select_cat(self, cid):
        self.selected_cat.set("" if self.selected_cat.get() == cid else cid)
        self._render_cat_grid()

    def _update_submit_btn(self):
        t = self.selected_type.get()
        if t == "income":
            self._submit_btn.config(bg=GREEN, fg="#000000")
        else:
            self._submit_btn.config(bg=RED, fg="#ffffff")

    def _submit(self):
        raw = self._amount_var.get().strip().replace(",", ".")
        try:
            amount = float(raw)
        except ValueError:
            messagebox.showerror("Gabim", "Fut një shumë të vlefshme numerike.", parent=self.root)
            return

        if not self.selected_cat.get():
            messagebox.showerror("Gabim", "Zgjidh një kategori.", parent=self.root)
            return

        date_str = self._date_var.get().strip() or date.today().isoformat()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Gabim", "Data duhet të jetë në formatin YYYY-MM-DD.", parent=self.root)
            return

        try:
            self.fm.add_transaction(
                tx_type=self.selected_type.get(),
                amount=amount,
                category=self.selected_cat.get(),
                description=self._desc_var.get(),
                date=date_str,
            )
        except ValueError as e:
            messagebox.showerror("Gabim", str(e), parent=self.root)
            return

        self._amount_var.set("")
        self._desc_var.set("")
        self.selected_cat.set("")
        self._render_cat_grid()
        self._refresh_header()
        self._refresh_tx_list()
        messagebox.showinfo(
            "Sukses",
            f"{'Të ardhurat' if self.selected_type.get() == 'income' else 'Shpenzimi'} u regjistrua!",
            parent=self.root,
        )

    # ── panel: transactions ───────────────────────────────────────────────────

    def _build_tx_panel(self, parent):
        frame = styled_frame(parent, bg=BG)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        # header row
        hdr = styled_frame(frame, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 8))

        label(hdr, "Transaksionet", font=("Segoe UI", 14, "bold"), bg=BG).pack(side="left")

        # month nav
        nav = styled_frame(hdr, bg=BG)
        nav.pack(side="right")
        tk.Button(nav, text="‹", font=FONT_B, bg=SURFACE2, fg=TEXT, relief="flat",
                  padx=10, cursor="hand2",
                  command=lambda: self._change_month(-1)).pack(side="left")
        self._month_lbl = label(nav, "", font=FONT, bg=BG)
        self._month_lbl.pack(side="left", padx=10)
        tk.Button(nav, text="›", font=FONT_B, bg=SURFACE2, fg=TEXT, relief="flat",
                  padx=10, cursor="hand2",
                  command=lambda: self._change_month(1)).pack(side="left")

        # filters
        flt = styled_frame(frame, bg=BG)
        flt.pack(fill="x", padx=28, pady=(0, 8))

        self._filter_type = tk.StringVar(value="all")
        self._filter_cat  = tk.StringVar(value="all")

        type_opts = [("all", "Të gjitha"), ("income", "Vetëm të ardhura"), ("expense", "Vetëm shpenzime")]
        type_menu = ttk.Combobox(
            flt, textvariable=self._filter_type, state="readonly", width=20, font=FONT,
            values=[v for _, v in type_opts],
        )
        type_menu.set("Të gjitha")
        type_menu.pack(side="left", padx=(0, 8))
        type_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_tx_list())

        cat_opts = ["Të gjitha kategoritë"] + [
            f"{m['icon']} {m['name']}" for m in ALL_CATEGORIES.values()
        ]
        cat_menu = ttk.Combobox(
            flt, textvariable=self._filter_cat, state="readonly", width=22, font=FONT,
            values=cat_opts,
        )
        cat_menu.set("Të gjitha kategoritë")
        cat_menu.pack(side="left")
        cat_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_tx_list())

        # scrollable list
        canvas_wrap = styled_frame(frame, bg=BG)
        canvas_wrap.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        canvas_wrap.rowconfigure(0, weight=1)
        canvas_wrap.columnconfigure(0, weight=1)

        self._tx_canvas = tk.Canvas(canvas_wrap, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self._tx_canvas.yview)
        self._tx_inner = styled_frame(self._tx_canvas, bg=BG)

        self._tx_inner.bind("<Configure>", lambda e: self._tx_canvas.configure(
            scrollregion=self._tx_canvas.bbox("all")
        ))
        self._tx_canvas.create_window((0, 0), window=self._tx_inner, anchor="nw")
        self._tx_canvas.configure(yscrollcommand=scrollbar.set)

        self._tx_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._tx_canvas.bind_all("<MouseWheel>", lambda e: self._tx_canvas.yview_scroll(
            -1 if e.delta > 0 else 1, "units"
        ))

        return frame

    def _change_month(self, direction):
        self.view_month += direction
        if self.view_month > 12:
            self.view_month = 1;  self.view_year += 1
        elif self.view_month < 1:
            self.view_month = 12; self.view_year -= 1
        self._refresh_header()
        self._refresh_tx_list()

    def _refresh_tx_list(self):
        months_sq = ["Janar","Shkurt","Mars","Prill","Maj","Qershor",
                     "Korrik","Gusht","Shtator","Tetor","Nëntor","Dhjetor"]
        self._month_lbl.config(text=f"{months_sq[self.view_month-1]} {self.view_year}")

        for w in self._tx_inner.winfo_children():
            w.destroy()

        # resolve filters
        raw_type = self._filter_type.get()
        type_map = {"Të gjitha": "all", "Vetëm të ardhura": "income", "Vetëm shpenzime": "expense"}
        tx_type = type_map.get(raw_type, "all")

        cat_filter = None
        raw_cat = self._filter_cat.get()
        if raw_cat and raw_cat != "Të gjitha kategoritë":
            for cid, meta in ALL_CATEGORIES.items():
                if f"{meta['icon']} {meta['name']}" == raw_cat:
                    cat_filter = cid
                    break

        txs = self.fm.get_transactions(
            month=self.view_month, year=self.view_year,
            tx_type=None if tx_type == "all" else tx_type,
            category=cat_filter,
        )

        if not txs:
            label(self._tx_inner, "Nuk ka transaksione.", font=FONT, fg=TEXT_SEC, bg=BG).pack(pady=32)
            return

        for tx in txs:
            self._render_tx_row(tx)

    def _render_tx_row(self, tx):
        color = CAT_COLORS.get(tx["category"], "#888")
        sign  = "+" if tx["type"] == "income" else "-"
        amt_c = GREEN if tx["type"] == "income" else RED

        row = styled_frame(self._tx_inner, bg=SURFACE)
        row.pack(fill="x", padx=4, pady=3)
        row.columnconfigure(1, weight=1)

        icon_lbl = label(row, tx["category_icon"], font=("Segoe UI", 18), bg=SURFACE)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=10)

        desc_text = tx.get("description") or tx["category_name"]
        label(row, desc_text, font=FONT_B, bg=SURFACE).grid(row=0, column=1, sticky="w", pady=(8, 0))
        label(
            row,
            f"{tx['category_name']} · {tx['date']}",
            font=FONT_SM, fg=TEXT_SEC, bg=SURFACE,
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        label(
            row, f"{sign}${tx['amount']:.2f}", font=FONT_B, fg=amt_c, bg=SURFACE
        ).grid(row=0, column=2, rowspan=2, padx=(0, 8))

        del_btn = tk.Button(
            row, text="✕", font=FONT_SM, bg=SURFACE, fg=TEXT_SEC, relief="flat",
            cursor="hand2", padx=6,
            command=lambda tid=tx["id"]: self._delete_tx(tid),
        )
        del_btn.grid(row=0, column=3, rowspan=2, padx=(0, 10))
        del_btn.bind("<Enter>", lambda e, b=del_btn: b.config(fg=RED))
        del_btn.bind("<Leave>", lambda e, b=del_btn: b.config(fg=TEXT_SEC))

    def _delete_tx(self, tx_id):
        if not messagebox.askyesno("Konfirmo", "Të fshihet ky transaksion?", parent=self.root):
            return
        try:
            self.fm.delete_transaction(tx_id)
        except ValueError as e:
            messagebox.showerror("Gabim", str(e), parent=self.root)
            return
        self._refresh_header()
        self._refresh_tx_list()

    # ── panel: stats ──────────────────────────────────────────────────────────

    def _build_stats_panel(self, parent):
        frame = styled_frame(parent, bg=BG)
        frame.columnconfigure(0, weight=1)

        label(frame, "Statistika", font=("Segoe UI", 14, "bold"), bg=BG).pack(
            anchor="w", padx=28, pady=(24, 4)
        )
        label(frame, f"Muaji aktual dhe ndarja sipas kategorisë",
              font=FONT_SM, fg=TEXT_SEC, bg=BG).pack(anchor="w", padx=28, pady=(0, 16))

        # summary cards
        cards_row = styled_frame(frame, bg=BG)
        cards_row.pack(fill="x", padx=24)

        self._stat_vars = {}
        for key, lbl, color in [
            ("income",  "Të ardhura",  GREEN),
            ("expense", "Shpenzime",   RED),
            ("net",     "Neto",        TEXT),
        ]:
            card = styled_frame(cards_row, bg=SURFACE)
            card.pack(side="left", expand=True, fill="x", padx=4)
            label(card, lbl, font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=16, pady=(14, 2))
            var = tk.StringVar(value="$0.00")
            label(card, "", font=("Segoe UI", 18, "bold"), fg=color, bg=SURFACE,
                  textvariable=var).pack(anchor="w", padx=16, pady=(0, 14))
            self._stat_vars[key] = var

        # bar chart canvas
        chart_card = styled_frame(frame, bg=SURFACE)
        chart_card.pack(fill="x", padx=24, pady=(12, 0))
        label(chart_card, "Të ardhura vs Shpenzime — 6 muajt e fundit",
              font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=16, pady=(12, 6))

        self._chart_canvas = tk.Canvas(chart_card, bg=SURFACE, highlightthickness=0, height=140)
        self._chart_canvas.pack(fill="x", padx=16, pady=(0, 14))
        self._chart_canvas.bind("<Configure>", lambda e: self._draw_bar_chart())

        # category breakdowns
        breakdown_row = styled_frame(frame, bg=BG)
        breakdown_row.pack(fill="both", expand=True, padx=24, pady=12)
        breakdown_row.columnconfigure(0, weight=1)
        breakdown_row.columnconfigure(1, weight=1)

        self._breakdown_frames = {}
        for col, key, title in [(0, "expense", "Shpenzime sipas kategorisë"),
                                 (1, "income",  "Të ardhura sipas kategorisë")]:
            card = styled_frame(breakdown_row, bg=SURFACE)
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            label(card, title, font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(
                anchor="w", padx=14, pady=(12, 6)
            )
            inner = styled_frame(card, bg=SURFACE)
            inner.pack(fill="both", expand=True, padx=14, pady=(0, 12))
            self._breakdown_frames[key] = inner

        return frame

    def _refresh_stats(self):
        summary = self.fm.monthly_summary(self.view_month, self.view_year)
        for key in ("income", "expense", "net"):
            val = summary[key]
            prefix = "-$" if (key == "net" and val < 0) else ("$" if key == "net" else
                               ("+" if key == "income" else "-") + "$")
            self._stat_vars[key].set(f"{prefix}{abs(val):.2f}")

        self._draw_bar_chart()
        self._render_category_breakdown()

    def _draw_bar_chart(self):
        c = self._chart_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return
        h = 120

        months_data = []
        for i in range(5, -1, -1):
            m = self.view_month - i
            y = self.view_year
            while m < 1:
                m += 12; y -= 1
            s = self.fm.monthly_summary(m, y)
            months_data.append(s)

        month_names = ["J","F","M","A","M","Q","K","G","Sh","T","N","D"]
        max_val = max((max(d["income"], d["expense"]) for d in months_data), default=1) or 1

        slot_w = w / 6
        bar_w  = slot_w * 0.28

        for i, d in enumerate(months_data):
            cx = slot_w * i + slot_w / 2
            for val, color, offset in [
                (d["income"], GREEN, -bar_w * 0.6),
                (d["expense"], RED,  bar_w * 0.6),
            ]:
                bar_h = (val / max_val) * (h - 24)
                x0 = cx + offset - bar_w / 2
                x1 = cx + offset + bar_w / 2
                y0 = h - bar_h - 16
                y1 = h - 16
                c.create_rectangle(x0, max(y0, 0), x1, y1, fill=color, outline="", width=0)

            c.create_text(
                cx, h - 4, text=month_names[(self.view_month - 6 + i) % 12],
                font=("Segoe UI", 8), fill=TEXT_SEC, anchor="s"
            )

    def _render_category_breakdown(self):
        for key, inner in self._breakdown_frames.items():
            for w in inner.winfo_children():
                w.destroy()

            data = self.fm.category_breakdown(key, self.view_month, self.view_year)
            total = sum(data.values()) or 1
            cats  = INCOME_CATEGORIES if key == "income" else EXPENSE_CATEGORIES

            if not data:
                label(inner, "Nuk ka të dhëna.", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).pack(anchor="w")
                continue

            for cid, amt in data.items():
                meta  = cats.get(cid, {"name": cid, "icon": "•"})
                color = CAT_COLORS.get(cid, "#888")
                pct   = int(amt / total * 100)

                row = styled_frame(inner, bg=SURFACE)
                row.pack(fill="x", pady=3)
                row.columnconfigure(1, weight=1)

                label(row, meta["icon"], font=("Segoe UI", 13), bg=SURFACE).grid(
                    row=0, column=0, padx=(0, 6), pady=2
                )
                label(row, meta["name"], font=FONT_SM, bg=SURFACE).grid(
                    row=0, column=1, sticky="w"
                )
                label(row, f"${amt:.2f}", font=FONT_SM, fg=TEXT_SEC, bg=SURFACE).grid(
                    row=0, column=2
                )

                bar_bg = styled_frame(inner, bg=SURFACE2, height=4)
                bar_bg.pack(fill="x", pady=(0, 2))
                bar_bg.pack_propagate(False)
                bar_fill = styled_frame(bar_bg, bg=color, height=4)
                bar_fill.place(relx=0, rely=0, relwidth=pct / 100, relheight=1)

    # ── navigation ────────────────────────────────────────────────────────────

    def _show_panel(self, key):
        for k, btn in self._nav_buttons.items():
            btn.config(
                bg=SURFACE2 if k == key else SURFACE,
                fg=TEXT     if k == key else TEXT_SEC,
            )
        for k, panel in self._panels.items():
            if k == key:
                panel.tkraise()

        if key == "transactions":
            self._refresh_tx_list()
        elif key == "stats":
            self._refresh_stats()

    # ── shared header refresh ─────────────────────────────────────────────────

    def _refresh_header(self):
        b = self.fm.balance
        self._sb_balance_var.set(f"{'−' if b < 0 else ''}${abs(b):.2f}")
        summary = self.fm.monthly_summary(self.view_month, self.view_year)
        self._sb_income_var.set(f"+${summary['income']:.2f}")
        self._sb_expense_var.set(f"-${summary['expense']:.2f}")

    # ── run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()