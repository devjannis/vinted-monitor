from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from utils.logger import logger


@dataclass
class Product:
    id: str
    title: str
    price: float
    url: str
    description: str
    photos: List[Dict]
    size_title: str
    total_reviews: int
    feedback_reputation: float
    brand: str
    condition: str
    country: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_api_response(cls, data: Dict) -> Optional["Product"]:
        try:
            item = data.get("item", {})
            price = item.get("price", {})
            if type(price) is dict:
                price = price.get("amount", 0)
            user = item.get("user", {})
            brand = item.get("brand_dto", {})
            return cls(
                id=str(item.get("id")),
                title=item.get("title", ""),
                price=price,
                url=item.get("url", ""),
                description=item.get("description", ""),
                photos=item.get("photos", []),
                size_title=item.get("size_title", ""),
                total_reviews=int(user.get("feedback_count", 0)),
                feedback_reputation=float(user.get("feedback_reputation", 0)),
                brand=brand.get("title", "Unknown"),
                condition=item.get("status", "Unknown"),
                country=user.get("country_title_local", "Unknown")
            )
        except Exception as e:
            logger.error(f"Error parsing product from API response: {str(e)}")
            return None