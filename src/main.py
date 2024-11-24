import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import discord
import requests
from discord import Embed, Activity, ActivityType
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vinted_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VintedConfig:
    token: str
    channel_id: int
    search_terms: List[str]
    refresh_delay: int = 3
    max_images_per_post: int = 4
    
    @classmethod
    def load(cls, path: str = "config.json") -> "VintedConfig":
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            logger.warning(f"Config file {path} not found, using default values")
            return cls(
                token=None,
                channel_id=0,
                search_terms=["ralph lauren"],
                refresh_delay=3,
                max_images_per_post=4
            )

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
    def from_api_response(cls, data: Dict) -> "Product":
        try:
            if not isinstance(data, dict):
                logger.error(f"Expected dictionary, got {type(data)}")
                return None
                
            # Get the item data
            item_data = data.get("item", {})
            if not isinstance(item_data, dict):
                logger.error(f"Expected item dictionary, got {type(item_data)}")
                return None
                
            # Get nested objects
            price_data = item_data.get("price", {})
            user_data = item_data.get("user", {})
            brand_data = item_data.get("brand_dto", {})
            
            
            return cls(
                id=str(item_data.get("id", "")),
                title=str(item_data.get("title", "")),
                price=float(price_data.get("amount", 0.0)) if isinstance(price_data, dict) else 0.0,
                url=str(item_data.get("url", "")),
                description=str(item_data.get("description", "")),
                photos=item_data.get("photos", []) if isinstance(item_data.get("photos"), list) else [],
                size_title=str(item_data.get("size_title", "")),
                total_reviews=int(user_data.get("feedback_count", 0)) if isinstance(user_data, dict) else 0,
                feedback_reputation=float(user_data.get("feedback_reputation", 0.0)) if isinstance(user_data, dict) else 0.0,
                brand=str(brand_data.get("title", "Unknown")) if isinstance(brand_data, dict) else "Unknown",
                condition=str(item_data.get("status", "Unknown")),
                country=str(user_data.get("country_title_local", "Unknown")) if isinstance(user_data, dict) else "Unknown"
            )
        except Exception as e:
            logger.error(f"Error creating Product from API response: {str(e)}")
            raise

class ProductDatabase:
    def __init__(self, file_path: str = "products.json"):
        self.file_path = Path(file_path)
        self.seen_products: Dict[str, Dict] = self._load_database()

    def _load_database(self) -> Dict[str, Dict]:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_database(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.seen_products, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")

    def is_product_seen(self, product_id: str) -> bool:
        return product_id in self.seen_products

    def add_product(self, product: Product):
        try:
            self.seen_products[product.id] = {
                "data": product.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            self.save_database()
        except Exception as e:
            logger.error(f"Error adding product to database: {str(e)}")

class VintedAPI:
    BASE_URL = "https://www.vinted.de"
    
    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
        
    def _get_headers(self, with_auth: bool = False) -> Dict:
        headers = {
            'Host': 'www.vinted.de',
            'x-app-version': '24.43.1',
            'accept': 'application/json',
            'accept-language': 'de-fr',
            'user-agent': 'vinted-ios Vinted/24.43.1 (lt.manodrabuziai.de; build:30115; iOS 18.2.0) iPad13,6',
            'x-device-model': 'iPad13,6'
        }
        
        if with_auth and self.token:
            headers['authorization'] = f'Bearer {self.token}'
            
        return headers
    
    async def authenticate(self) -> bool:
        try:
            response = requests.post(
                f'{self.BASE_URL}/oauth/token',
                headers=self._get_headers(),
                json={
                    'grant_type': 'password',
                    'scope': 'public',
                    'client_id': 'ios',
                }
            )
            response.raise_for_status()
            self.token = response.json()['access_token']
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    async def search_products(self, search_text: str) -> List[Dict]:
        try:
            params = {
                'page': '1',
                'per_page': '10',
                'search_text': search_text,
                'order': 'newest_first',
            }
            
            response = self.session.get(
                f'{self.BASE_URL}/api/v2/catalog/items',
                params=params,
                headers=self._get_headers(with_auth=True)
            )
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            return []

    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        try:
            response = self.session.get(
                f'{self.BASE_URL}/api/v2/items/{product_id}/details',
                headers=self._get_headers(with_auth=True)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get product details for ID {product_id}: {str(e)}")
            return None

class DiscordView(discord.ui.View):
    def __init__(self, product: Product):
        super().__init__()
        
        # Add buttons
        self.add_item(discord.ui.Button(
            label='Buy Now',
            style=discord.ButtonStyle.link,
            url=f"https://www.vinted.de/transaction/buy/new?source_screen=item&transaction%5Bitem_id%5D={product.id}"
        ))
        
        self.add_item(discord.ui.Button(
            label='Send Message',
            style=discord.ButtonStyle.link,
            url=f"https://www.vinted.de/items/{product.id}/want_it/new?button_name=receiver_id={product.id}"
        ))
        
        self.add_item(discord.ui.Button(
            label='Open Product',
            style=discord.ButtonStyle.link,
            url=product.url
        ))

class VintedMonitor(discord.Client):
    def __init__(self, config: VintedConfig):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(intents=intents)
        
        self.config = config
        self.api = VintedAPI()
        self.db = ProductDatabase()
        self.country_flags = {
            "Deutschland": "🇩🇪", "Frankreich": "🇫🇷", "Spanien": "🇪🇸",
            "Italien": "🇮🇹", "Österreich": "🇦🇹", "Schweiz": "🇨🇭",
            "Niederlande": "🇳🇱", "Belgien": "🇧🇪", "Portugal": "🇵🇹",
            "Vereinigtes Königreich": "🇬🇧"
        }

    def create_embeds(self, product: Product) -> List[Embed]:
        try:
            stars = 1 + 4 * product.feedback_reputation
            
            main_embed = Embed(title=product.title, url=product.url, color=0x000000)
            main_embed.description = product.description
            main_embed.add_field(name="Price", value=f"{product.price} €", inline=True)
            main_embed.add_field(name="Size", value=product.size_title, inline=True)
            main_embed.add_field(name="Brand", value=product.brand, inline=True)
            main_embed.add_field(name="Country", value=self.country_flags.get(product.country, "🏳️"), inline=True)
            main_embed.add_field(name="User Rating", value=f"({round(stars, 2)}) of {product.total_reviews}", inline=True)
            main_embed.add_field(name="Condition", value=product.condition, inline=True)
            
            if product.photos and len(product.photos) > 0:
                main_embed.set_image(url=product.photos[0].get("url", ""))
            
            main_embed.set_footer(text="Vinted Monitor")

            embeds = [main_embed]
            
            # Add additional photo embeds
            for photo in product.photos[1:self.config.max_images_per_post]:
                if photo_url := photo.get("url"):
                    embed = Embed(url=product.url)
                    embed.set_image(url=photo_url)
                    embeds.append(embed)
                
            return embeds
        except Exception as e:
            logger.error(f"Error creating embeds: {str(e)}")
            return []

    async def start_monitoring(self):
        while True:
            try:
                if not self.api.token and not await self.api.authenticate():
                    logger.warning("Authentication failed, retrying in 30 seconds...")
                    await asyncio.sleep(30)
                    continue

                for search_term in self.config.search_terms:
                    logger.debug(f"Searching for term: {search_term}")
                    items = await self.api.search_products(search_term)
                    
                    for item in items:
                        try:
                            item_id = str(item.get('id'))
                            if not item_id or self.db.is_product_seen(item_id):
                                continue
                                
                            details = await self.api.get_product_details(item_id)
                            if not details:
                                continue
                                
                            product = Product.from_api_response(details)
                            if product.country != "Deutschland":
                                continue
                                
                            self.db.add_product(product)
                            
                            channel = self.get_channel(self.config.channel_id)
                            if channel:
                                embeds = self.create_embeds(product)
                                if embeds:
                                    await channel.send(embeds=embeds, view=DiscordView(product))
                                    logger.info(f"New product found and posted: {product.title}")
                        except Exception as e:
                            logger.error(f"Error processing item: {str(e)}")
                            continue

                await asyncio.sleep(self.config.refresh_delay)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(30)

    async def on_ready(self):
        activity = Activity(name="Vinted Monitor", type=ActivityType.watching)
        await self.change_presence(activity=activity)
        logger.info(f"Logged in as {self.user}")
        
        await self.start_monitoring()

def main():
    try:
        config = VintedConfig.load()
        client = VintedMonitor(config)
        client.run(config.token)
    except Exception as e:
        logger.critical(f"Failed to start the bot: {str(e)}")

if __name__ == "__main__":
    main()
