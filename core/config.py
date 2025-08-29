import os, json

ROOT = os.path.dirname(os.path.dirname(__file__))
CFG = os.path.join(ROOT, "config.json")
DEFAULTS = {
    "market_name": None,
    "low_stock_limit": 5,
    "csv_path": os.path.join(ROOT, "inventory.csv"),
}

class Config:
    def __init__(self, path=CFG):
        self.path = path
        self.data = DEFAULTS.copy()
        if os.path.exists(path):
            try:
                self.data.update(json.load(open(path, 'r', encoding='utf-8')))
            except Exception:
                pass
    def save(self):
        json.dump(self.data, open(self.path, 'w', encoding='utf-8'), indent=2)
