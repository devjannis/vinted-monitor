import discord
import asyncio
from api.vinted import VintedAPI
from models.config import VintedConfig
from models.database import ProductDatabase
from models.product import Product
from discord_utils.views import DiscordView
from discord_utils.embeds import create_embeds
from utils.logger import logger


class VintedMonitor(discord.Client):
    def __init__(self, config: VintedConfig):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.config = config
        self.api = VintedAPI()
        self.db = ProductDatabase()
        self.flags = {
            "Deutschland": "🇩🇪",
            "Frankreich": "🇫🇷",
            "Spanien": "🇪🇸",
            "Italien": "🇮🇹",
            "Österreich": "🇦🇹",
            "Schweiz": "🇨🇭",
            "Niederlande": "🇳🇱",
            "Belgien": "🇧🇪",
            "Portugal": "🇵🇹",
            "Vereinigtes Königreich": "🇬🇧"
        }

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="Vinted Monitor", type=discord.ActivityType.watching))
        logger.info(f"Logged in as {self.user}")
        await self.start_monitoring()

    async def start_monitoring(self):
        while True:
            if not self.api.token and not await self.api.authenticate():
                await asyncio.sleep(30)
                continue

            for term in self.config.search_terms:
                items = await self.api.search_products(term)
                for item in items:
                    item_id = str(item.get("id"))
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
                        embeds = create_embeds(product, self.config.max_images_per_post, self.flags)
                        await channel.send(embeds=embeds, view=DiscordView(product))
                        logger.info(f"Posted: {product.title}")

            await asyncio.sleep(self.config.refresh_delay)
