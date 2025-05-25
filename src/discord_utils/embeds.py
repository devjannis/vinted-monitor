from discord import Embed
from typing import List
from models.product import Product


def create_embeds(product: Product, max_images: int, flags: dict) -> List[Embed]:
    stars = 1 + 4 * product.feedback_reputation
    embed = Embed(title=product.title, url=product.url)
    embed.description = product.description
    embed.add_field(name="Price", value=f"{product.price} €", inline=True)
    embed.add_field(name="Size", value=product.size_title, inline=True)
    embed.add_field(name="Brand", value=product.brand, inline=True)
    embed.add_field(name="Country", value=flags.get(product.country, "🏳️"), inline=True)
    embed.add_field(name="User Rating", value=f"({round(stars, 2)}) of {product.total_reviews}", inline=True)
    embed.add_field(name="Condition", value=product.condition, inline=True)
    if product.photos:
        embed.set_image(url=product.photos[0].get("url", ""))
    embed.set_footer(text="Vinted Monitor")

    embeds = [embed]
    for photo in product.photos[1:max_images]:
        url = photo.get("url")
        if url:
            photo_embed = Embed(url=product.url)
            photo_embed.set_image(url=url)
            embeds.append(photo_embed)

    return embeds