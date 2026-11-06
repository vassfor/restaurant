import json
from pathlib import Path


class BusinessDataStore:
    def __init__(self, path="business_data.json"):
        self.path = Path(path)

    def exists(self):
        return self.path.exists()

    def load(self):
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, business_name, tables):
        payload = {
            "business_name": business_name,
            "table_no": str(len(tables)),
            "tables": [[table.name, table.capacity] for table in tables],
        }
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=4)

    def business_name(self):
        return self.load()["business_name"]

    def tables(self):
        from models import Table
        return [Table(name, int(capacity)) for name, capacity in self.load()["tables"]]
