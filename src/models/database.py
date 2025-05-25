import json
from pathlib import Path
from typing import Dict
from datetime import datetime
from models.product import Product
from utils.logger import logger


class ProductDatabase:
    def __init__(self, file_path: str = "products.json"):
        self.file_path = Path(file_path)
        self.seen_products: Dict[str, Dict] = self._load()

    def _load(self) -> Dict[str, Dict]:
        if self.file_path.exists():
            return json.loads(self.file_path.read_text())
        return {}

    def save(self):
        self.file_path.write_text(json.dumps(self.seen_products, indent=2))

    def is_product_seen(self, product_id: str) -> bool:
        return product_id in self.seen_products

    def add_product(self, product: Product):
        self.seen_products[product.id] = {
            "data": product.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        self.save()