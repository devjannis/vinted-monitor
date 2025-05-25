import discord
from models.product import Product


class DiscordView(discord.ui.View):
    def __init__(self, product: Product):
        super().__init__()
        self.add_item(discord.ui.Button(label='Buy Now', style=discord.ButtonStyle.link, url=f"https://www.vinted.de/transaction/buy/new?transaction%5Bitem_id%5D={product.id}"))
        self.add_item(discord.ui.Button(label='Send Message', style=discord.ButtonStyle.link, url=f"https://www.vinted.de/items/{product.id}/want_it/new"))
        self.add_item(discord.ui.Button(label='Open Product', style=discord.ButtonStyle.link, url=product.url))
