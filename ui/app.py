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
        self.store = Store(self.cfg.data["csv_path"], self.cfg.data["log_path"])
        self._build_ui(); self.refresh()

    def _build_ui(self):
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
        frm = ttk.LabelFrame(self, text="Mobile Device", padding=10); frm.pack(fill='x', padx=12, pady=6)
        self.v_model, self.v_memory, self.v_cpu, self.v_price, self.v_stock = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
        def row(lbl, var, w, col):
            ttk.Label(frm, text=lbl).grid(row=0, column=col, sticky='w');
            ttk.Entry(frm, textvariable=var, width=w).grid(row=1, column=col, padx=(0,12))
        row("Model", self.v_model, 18, 0)
        row("Memory", self.v_memory, 10, 1)
        row("CPU", self.v_cpu, 10, 2)
        row("Price", self.v_price, 8, 3)
        row("Stock", self.v_stock, 8, 4)
        btns = ttk.Frame(frm); btns.grid(row=1, column=5)
        ttk.Button(btns, text="Add/Update", command=self.add_update).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Delete", command=self.delete).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="Sell", command=self.sell_item).grid(row=0, column=3, padx=4)
        # search
        s = ttk.LabelFrame(self, text="Search", padding=10); s.pack(fill='x', padx=12, pady=(0,6))
        self.v_search = tk.StringVar(); ttk.Label(s, text="Filter (model/memory/cpu):").pack(side='left')
        ttk.Entry(s, textvariable=self.v_search, width=40).pack(side='left', padx=(8,8))
        ttk.Button(s, text="Clear", command=lambda: self.v_search.set('')).pack(side='left')
        self.v_search.trace_add('write', lambda *_: self.refresh())
        # table
        wrap = ttk.Frame(self, padding=(12,6)); wrap.pack(fill='both', expand=True)
        cols = ("model","memory","cpu","price","stock","sold")
        self.tree = ttk.Treeview(wrap, columns=cols, show='headings', selectmode='browse')
        for c, t in zip(cols, ["Model","Memory","CPU","Price","Stock","Sold Count"]): self.tree.heading(c, text=t)
        self.tree.column("model", width=120); self.tree.column("memory", width=80)
        self.tree.column("cpu", width=80)
        self.tree.column("price", width=60, anchor='e')
        self.tree.column("stock", width=60, anchor='e')
        self.tree.column("sold", width=60, anchor='e')
        y = ttk.Scrollbar(wrap, orient='vertical', command=self.tree.yview); self.tree.configure(yscrollcommand=y.set)
        self.tree.pack(side='left', fill='both', expand=True); y.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        # footer
        foot = ttk.Frame(self, padding=(12,8)); foot.pack(fill='x')
        ttk.Button(foot, text="Export CSV...", command=self.export_csv).pack(side='left')
        ttk.Button(foot, text="Import CSV...", command=self.import_csv).pack(side='left', padx=(8,0))
        ttk.Button(foot, text="Report", command=self.show_report).pack(side='right')

    # actions
    def add_update(self):
        model = self.v_model.get().strip()
        memory = self.v_memory.get().strip()
        cpu = self.v_cpu.get().strip()
        try:
            price = float(self.v_price.get()); assert price >= 0
            stock = int(self.v_stock.get()); assert stock >= 0
        except Exception:
            messagebox.showwarning("Validation", "Price and Stock must be a numbers >=0"); return
        if not model: messagebox.showwarning("Validation", "Model required"); return
        try:
            self.store.upsert(model, memory, cpu, price, stock)
            self.refresh(select=model); self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    def delete(self):
        sel = self._selected_model()
        if not sel: messagebox.showinfo("Delete", "Select a row"); return
        if not messagebox.askyesno("Confirm", f"Delete '{sel}'?"): return
        try:
            self.store.delete(sel); self.refresh(); self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")
    def select_item(self):
        sel = self._selected_model()
        if not sel: messagebox.showinfo("Select", "Select a row"); return
        self.store.select(sel)
        self.refresh(select=sel)
    def sell_item(self):
        sel = self._selected_model()
        if not sel: messagebox.showinfo("Sell", "Select a row"); return
        qty = simpledialog.askinteger("Sell", "How many to sell?", parent=self, minvalue=1)
        if not qty: return
        self.store.sell(sel, qty)
        self.refresh(select=sel)
    def show_report(self):
        import csv
        from tkinter import filedialog, messagebox
        rep = self.store.get_report()
        total_value = sum(it['price'] * it.get('stock',0) for it in rep['items'])
        msg = f"Total mobiles: {rep['count']}\nTotal value: ${total_value:,.2f}\nTotal stock: {rep['total_stock']}\nTotal sold: {rep['total_sold']}\n\n"
        msg += "Model | Memory | CPU | Price | Stock | Sold\n" + "-"*50 + "\n"
        for it in rep['items']:
            msg += f"{it['model']} | {it['memory']} | {it['cpu']} | ${it['price']:.2f} | {it.get('stock',0)} | {it.get('sold',0)}\n"
        def export_csv():
            path = filedialog.asksaveasfilename(title="Export Report CSV", defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="report.csv")
            if not path: return
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["Model","Memory","CPU","Price","Stock","Sold"])
                for it in rep['items']:
                    w.writerow([it['model'], it['memory'], it['cpu'], f"{it['price']:.2f}", it.get('stock',0), it.get('sold',0)])
        if messagebox.askyesno("Report", msg + "\n\nExport to CSV? (Yes/No)"):
            export_csv()
        else:
            messagebox.showinfo("Report", msg)
    def on_select(self, _e=None):
        iid = next(iter(self.tree.selection()), None)
        if not iid: return
        m,mem,cpu,p,stock,sold = self.tree.item(iid,'values')
        self.v_model.set(m); self.v_memory.set(mem); self.v_cpu.set(cpu); self.v_price.set(p); self.v_stock.set(stock)
    def clear_form(self):
        for v in (self.v_model, self.v_memory, self.v_cpu, self.v_price, self.v_stock): v.set('')
    def export_csv(self):
        path = filedialog.asksaveasfilename(title="Export CSV", defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="export.csv")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f); w.writerow(["model","memory","cpu","price"])
                for it in self.store.list(): w.writerow([it['model'], it['memory'], it['cpu'], f"{it['price']:.2f}"])
            messagebox.showinfo("Export", "Done")
        except Exception as e:
            messagebox.showerror("Export", f"Failed: {e}")
    def import_csv(self):
        path = filedialog.askopenfilename(title="Import CSV", filetypes=[("CSV","*.csv"),("All","*.*")])
        if not path: return
        try:
            for row in csv.DictReader(open(path, 'r', newline='', encoding='utf-8')):
                model = (row.get('model') or '').strip()
                memory = (row.get('memory') or '').strip()
                cpu = (row.get('cpu') or '').strip()
                try:
                    price = float(row.get('price', 0.0))
                except Exception:
                    continue
                if model: self.store.upsert(model, memory, cpu, price)
            self.refresh(); messagebox.showinfo("Import", "Done")
        except Exception as e:
            messagebox.showerror("Import", f"Failed: {e}")

    # helpers
    def refresh(self, select: str|None=None):
        for r in self.tree.get_children(): self.tree.delete(r)
        q = (self.v_search.get() or '').lower().strip(); items = self.store.list()
        low_limit = int(self.cfg.data.get('low_stock_limit', 5))
        if q:
            items = [i for i in items if q in i['model'].lower() or q in i['memory'].lower() or q in i['cpu'].lower()]
        total = 0.0
        for it in items:
            value = it['price'] * it.get('stock',0)
            total += value
            tags = ('low',) if it.get('stock',0) <= low_limit else ()
            self.tree.insert('', 'end', values=(it['model'], it['memory'], it['cpu'], round(it['price'],2), it.get('stock',0), it.get('sold',0)), tags=tags)
        self.tree.tag_configure('low', foreground='#b00000', font=('Segoe UI', 9, 'bold'))
        self.lbl_total.config(text=f"Total: ${total:,.2f}")
        if select:
            for r in self.tree.get_children():
                if self.tree.item(r,'values')[0].lower()==select.lower(): self.tree.selection_set(r); self.tree.see(r); break
    def _selected_model(self):
        iid = next(iter(self.tree.selection()), None)
        return self.tree.item(iid, 'values')[0] if iid else None
    def open_settings(self):
        dlg = SettingsDialog(self, self.cfg); self.wait_window(dlg)
        if not dlg.result: return
        self.cfg.data.update(dlg.result); self.cfg.save()
        self.lbl_market.config(text=f"Market: {self.cfg.data['market_name']}")
        self.refresh()
