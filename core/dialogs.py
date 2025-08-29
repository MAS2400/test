import tkinter as tk
from tkinter import ttk, messagebox

class SettingsDialog(tk.Toplevel):
    def __init__(self, master, cfg):
        super().__init__(master); self.title("Settings"); self.resizable(False, False); self.result=None; self.grab_set()
        v_name = tk.StringVar(value=cfg.data.get("market_name") or "")
        v_low = tk.StringVar(value=str(cfg.data.get("low_stock_limit", 5)))
        f = ttk.Frame(self, padding=10); f.grid()
        ttk.Label(f, text="Market Name:").grid(row=0, column=0, sticky='w')
        e1 = ttk.Entry(f, textvariable=v_name, width=36); e1.grid(row=0, column=1, pady=(0,8))
        ttk.Label(f, text="Low-stock limit:").grid(row=1, column=0, sticky='w')
        e2 = ttk.Entry(f, textvariable=v_low, width=12); e2.grid(row=1, column=1)
        btn = ttk.Frame(f); btn.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn, text="Save", command=lambda: self._save(v_name.get(), v_low.get())).grid(row=0, column=0, padx=5)
        ttk.Button(btn, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=5)
        e1.focus_set(); self.bind('<Return>', lambda _e: self._save(v_name.get(), v_low.get()))
    def _save(self, name, low):
        try:
            low = int(low); assert low >= 0
        except Exception:
            messagebox.showwarning("Validation", "Low-stock limit must be a non-negative integer"); return
        self.result = {"market_name": name.strip(), "low_stock_limit": low}; self.destroy()
