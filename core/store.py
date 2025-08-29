import os, csv

class Store:
    # Schema: name, category, quantity, price
    def __init__(self, csv_path: str):
        self.path = csv_path
        self.init()
    def init(self):
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["name", "category", "quantity", "price"])
        else:
            try:
                with open(self.path, 'r', newline='', encoding='utf-8') as f:
                    r = csv.reader(f); header = next(r, [])
                if "category" not in [h.strip().lower() for h in header]:
                    items = self.list(); self._write_all(items)
            except Exception:
                pass
    def list(self):
        items = []
        with open(self.path, 'r', newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    items.append({
                        "name": row.get("name", ""),
                        "category": row.get("category", ""),
                        "quantity": int(row.get("quantity", 0)),
                        "price": float(row.get("price", 0.0)),
                    })
                except Exception:
                    pass
        return items
    def _write_all(self, items):
        with open(self.path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(["name", "category", "quantity", "price"])
            for it in items:
                w.writerow([it["name"], it.get("category",""), it["quantity"], f"{it['price']:.2f}"])
    def upsert(self, name, category, quantity, price):
        items = self.list(); found = False
        for it in items:
            if it["name"].lower() == name.lower():
                it.update({"category": category, "quantity": quantity, "price": price}); found = True; break
        if not found:
            items.append({"name": name, "category": category, "quantity": quantity, "price": price})
        self._write_all(items)
    def delete(self, name):
        items = [it for it in self.list() if it["name"].lower() != name.lower()]
        self._write_all(items)
