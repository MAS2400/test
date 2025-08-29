import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from core.config import Config
from core.store import Store
from core.dialogs import SettingsDialog
import csv

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Market Warehousing"); self.geometry("820x500"); self.minsize(740, 460)
        self.cfg = Config()
        if not self.cfg.data["market_name"]:
            name = simpledialog.askstring("Market", "Enter market name:", parent=self)
            if not name: self.destroy(); return
            self.cfg.data["market_name"] = name.strip(); self.cfg.save()
        self.store = Store(self.cfg.data["csv_path"])
        self._build_ui(); self.refresh()

    def _build_ui(self):
        # ...existing code for building UI (copy from original)...
        # menu
        m = tk.Menu(self)
        appm = tk.Menu(m, tearoff=0)
        appm.add_command(label="Settings...", command=self.open_settings)
        appm.add_separator(); appm.add_command(label="Exit", command=self.destroy)
        m.add_cascade(label="App", menu=appm); self.config(menu=m)
        # header
        top = ttk.Frame(self, padding=(12,8)); top.pack(fill='x')
        self.lbl_market = ttk.Label(top, text=f"Market: {self.cfg.data['market_name']}", font=('Segoe UI', 12, 'bold'))
        self.lbl_market.pack(side='left')
        self.lbl_total = ttk.Label(top, text="Total: $0.00", font=('Segoe UI', 11))
        self.lbl_total.pack(side='right')
        # form
        frm = ttk.LabelFrame(self, text="Item", padding=10); frm.pack(fill='x', padx=12, pady=6)
        self.v_name, self.v_cat, self.v_qty, self.v_price = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
        def row(lbl, var, w, col):
            ttk.Label(frm, text=lbl).grid(row=0, column=col, sticky='w');
            ttk.Entry(frm, textvariable=var, width=w).grid(row=1, column=col, padx=(0,12))
        row("Name", self.v_name, 26, 0)
        row("Category", self.v_cat, 16, 1)
        row("Qty", self.v_qty, 8, 2)
        row("Price", self.v_price, 10, 3)
        btns = ttk.Frame(frm); btns.grid(row=1, column=4)
        ttk.Button(btns, text="Add/Update", command=self.add_update).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Delete", command=self.delete).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).grid(row=0, column=2, padx=4)
        # search
        s = ttk.LabelFrame(self, text="Search", padding=10); s.pack(fill='x', padx=12, pady=(0,6))
        self.v_search = tk.StringVar(); ttk.Label(s, text="Filter (name/category):").pack(side='left')
        ttk.Entry(s, textvariable=self.v_search, width=40).pack(side='left', padx=(8,8))
        ttk.Button(s, text="Clear", command=lambda: self.v_search.set('')).pack(side='left')
        self.v_search.trace_add('write', lambda *_: self.refresh())
        # table
        wrap = ttk.Frame(self, padding=(12,6)); wrap.pack(fill='both', expand=True)
        cols = ("name","category","quantity","price","value")
        self.tree = ttk.Treeview(wrap, columns=cols, show='headings', selectmode='browse')
        for c, t in zip(cols, ["Name","Category","Qty","Price","Value"]): self.tree.heading(c, text=t)
        self.tree.column("name", width=220); self.tree.column("category", width=140)
        self.tree.column("quantity", width=60, anchor='e'); self.tree.column("price", width=80, anchor='e')
        self.tree.column("value", width=100, anchor='e')
        y = ttk.Scrollbar(wrap, orient='vertical', command=self.tree.yview); self.tree.configure(yscrollcommand=y.set)
        self.tree.tag_configure('low', foreground='#b00000', font=('Segoe UI', 9, 'bold'))
        self.tree.pack(side='left', fill='both', expand=True); y.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        # footer
        foot = ttk.Frame(self, padding=(12,8)); foot.pack(fill='x')
        ttk.Button(foot, text="Export CSV...", command=self.export_csv).pack(side='left')
        ttk.Button(foot, text="Import CSV...", command=self.import_csv).pack(side='left', padx=(8,0))

    # actions
    def add_update(self):
        name = self.v_name.get().strip(); cat = self.v_cat.get().strip()
        try:
            qty = int(self.v_qty.get()); price = float(self.v_price.get()); assert qty >= 0 and price >= 0
        except Exception:
            messagebox.showwarning("Validation", "Quantity must be int >=0 and price must be number >=0"); return
        if not name: messagebox.showwarning("Validation", "Name required"); return
        try:
            self.store.upsert(name, cat, qty, price); self.refresh(select=name); self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    def delete(self):
        sel = self._selected_name()
        if not sel: messagebox.showinfo("Delete", "Select a row"); return
        if not messagebox.askyesno("Confirm", f"Delete '{sel}'?"): return
        try:
            self.store.delete(sel); self.refresh(); self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")
    def on_select(self, _e=None):
        iid = next(iter(self.tree.selection()), None)
        if not iid: return
        n,c,q,p,_ = self.tree.item(iid,'values'); self.v_name.set(n); self.v_cat.set(c); self.v_qty.set(q); self.v_price.set(p)
    def clear_form(self):
        for v in (self.v_name, self.v_cat, self.v_qty, self.v_price): v.set('')
    def export_csv(self):
        path = filedialog.asksaveasfilename(title="Export CSV", defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="export.csv")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f); w.writerow(["name","category","quantity","price"])
                for it in self.store.list(): w.writerow([it['name'], it.get('category',''), it['quantity'], f"{it['price']:.2f}"])
            messagebox.showinfo("Export", "Done")
        except Exception as e:
            messagebox.showerror("Export", f"Failed: {e}")
    def import_csv(self):
        path = filedialog.askopenfilename(title="Import CSV", filetypes=[("CSV","*.csv"),("All","*.*")])
        if not path: return
        try:
            for row in csv.DictReader(open(path, 'r', newline='', encoding='utf-8')):
                name = (row.get('name') or '').strip(); cat = (row.get('category') or '').strip()
                try:
                    qty = int(row.get('quantity', 0)); price = float(row.get('price', 0.0))
                except Exception:
                    continue
                if name: self.store.upsert(name, cat, qty, price)
            self.refresh(); messagebox.showinfo("Import", "Done")
        except Exception as e:
            messagebox.showerror("Import", f"Failed: {e}")

    # helpers
    def refresh(self, select: str|None=None):
        for r in self.tree.get_children(): self.tree.delete(r)
        q = (self.v_search.get() or '').lower().strip(); items = self.store.list()
        if q: items = [i for i in items if q in i['name'].lower() or q in i.get('category','').lower()]
        total = 0.0; low = int(self.cfg.data.get('low_stock_limit', 5))
        for it in items:
            val = it['quantity'] * it['price']; total += val
            tags = ('low',) if it['quantity'] <= low else ()
            self.tree.insert('', 'end', values=(it['name'], it.get('category',''), it['quantity'], round(it['price'],2), round(val,2)), tags=tags)
        self.lbl_total.config(text=f"Total: ${total:,.2f}")
        if select:
            for r in self.tree.get_children():
                if self.tree.item(r,'values')[0].lower()==select.lower(): self.tree.selection_set(r); self.tree.see(r); break
    def _selected_name(self):
        iid = next(iter(self.tree.selection()), None)
        return self.tree.item(iid, 'values')[0] if iid else None
    def open_settings(self):
        dlg = SettingsDialog(self, self.cfg); self.wait_window(dlg)
        if not dlg.result: return
        self.cfg.data.update(dlg.result); self.cfg.save()
        self.lbl_market.config(text=f"Market: {self.cfg.data['market_name']}")
        self.refresh()
