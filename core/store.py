import os, csv
from core.logger import Logger

class Store:
    # Schema: model, memory, cpu, price, stock, sold
    def __init__(self, csv_path: str, log_path: str):
        self.path = csv_path
        self.logger = Logger(log_path)
        self.init()
    def init(self):
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["model", "memory", "cpu", "price", "stock", "sold"])
    def list(self):
        items = []
        with open(self.path, 'r', newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    items.append({
                        "model": row.get("model", ""),
                        "memory": row.get("memory", ""),
                        "cpu": row.get("cpu", ""),
                        "price": float(row.get("price", 0.0)),
                        "stock": int(row.get("stock", 0)),
                        "sold": int(row.get("sold", 0)),
                    })
                except Exception:
                    pass
        return items
    def _write_all(self, items):
        with open(self.path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["model", "memory", "cpu", "price", "stock", "sold"])
            for it in items:
                w.writerow([it["model"], it["memory"], it["cpu"], f"{it['price']:.2f}", it.get("stock", 0), it.get("sold", 0)])
    def upsert(self, model, memory, cpu, price, stock=0, sold=0):
        items = self.list(); found = False
        for it in items:
            if it["model"].lower() == model.lower():
                it.update({"memory": memory, "cpu": cpu, "price": price, "stock": stock, "sold": sold}); found = True
                self.logger.log("update", model, memory, cpu, price, f"Updated item, stock={stock}, sold={sold}")
                break
        if not found:
            items.append({"model": model, "memory": memory, "cpu": cpu, "price": price, "stock": stock, "sold": sold})
            self.logger.log("add", model, memory, cpu, price, f"Added item, stock={stock}, sold={sold}")
        self._write_all(items)
    def sell(self, model, qty=1):
        items = self.list()
        for it in items:
            if it["model"].lower() == model.lower():
                if it["stock"] >= qty:
                    it["stock"] -= qty
                    it["sold"] += qty
                    self.logger.log("sell", it["model"], it["memory"], it["cpu"], it["price"], f"Sold {qty}, stock now {it['stock']}, sold now {it['sold']}")
                else:
                    self.logger.log("sell_failed", it["model"], it["memory"], it["cpu"], it["price"], f"Sell failed, not enough stock")
        self._write_all(items)
    # select method removed; selling is now tracked by 'sold'
    def get_report(self):
        items = self.list()
        total_price = sum(it["price"] for it in items)
        total_sold = sum(it["sold"] for it in items)
        total_stock = sum(it["stock"] for it in items)
        return {
            "count": len(items),
            "total_price": total_price,
            "total_sold": total_sold,
            "total_stock": total_stock,
            "items": items
        }
    def delete(self, model):
        items = self.list()
        for it in items:
            if it["model"].lower() == model.lower():
                self.logger.log("delete", it["model"], it["memory"], it["cpu"], it["price"], "Deleted item")
        items = [it for it in items if it["model"].lower() != model.lower()]
        self._write_all(items)
