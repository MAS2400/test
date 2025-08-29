import csv, os

class Logger:
    def __init__(self, log_path):
        self.path = log_path
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(["action", "model", "memory", "cpu", "price", "details"])
    def log(self, action, model, memory, cpu, price, details=""):
        with open(self.path, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([action, model, memory, cpu, price, details])
