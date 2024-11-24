# Vinted Monitor Bot

A Discord bot that monitors Vinted for new products based on specific search terms. When new items are found, the bot posts them to a specified Discord channel with detailed information and links to the product.

## Features

- **Search for products** on Vinted based on configurable search terms.
- **Post new products** to a Discord channel with detailed information:
  - Product title, price, size, brand, country of origin, and condition.
  - User feedback rating.
  - A maximum of 4 product images.
- **Buttons for interaction:**
  - Buy now.
  - Send a message to the seller.
  - Direct link to the product on Vinted.
- **Customizable search terms** and refresh delay settings.
- **Stores seen products** to avoid duplicates using a local database (products.json).

## Requirements

- Python 3.7 or higher
- Dependencies:
  - `discord.py` (for interacting with Discord)
  - `requests` (for making HTTP requests)
  - `asyncio` (for handling asynchronous tasks)
  
To install the dependencies, use the following command:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/devjannis/vinted-monitor.git
   cd vinted-monitor
   ```

2. Create a `config.json` file with your configuration:

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "channel_id": 123456789012345678,
  "search_terms": ["ralph lauren", "nike"],
  "refresh_delay": 3,
  "max_images_per_post": 4
}
```

- Replace `YOUR_DISCORD_BOT_TOKEN` with your Discord bot token.
- Replace `123456789012345678` with the channel ID where the bot will post products.
- Adjust the `search_terms` to match the products you're looking for.
- Set the `refresh_delay` (in seconds) to control how often the bot checks for new products.

3. Create a `products.json` file to store seen products (this will be automatically generated if it doesn't exist):
   ```json
   {}
   ```

## Running the Bot

Run the bot with the following command:

```bash
python vinted_monitor.py
```

The bot will log in to Discord, authenticate with the Vinted API, and begin monitoring the products. If new items matching your search terms are found, they will be posted in the specified channel.

## Logging

The bot logs activity to a file named `vinted_monitor.log` and the console. It logs:

- Successful product posts
- Errors (e.g., issues with authentication, retrieving product data, etc.)

## Commands and Buttons

Once the bot posts a product in the Discord channel, the following buttons will be available for interaction:

- **Buy Now**: Opens the Vinted purchase page for the product.
- **Send Message**: Opens the messaging page to contact the seller.
- **Open Product**: Directly opens the product page on Vinted.

## Customization

You can customize several aspects of the bot by modifying the `config.json` file:

- **search_terms**: A list of keywords to search for products.
- **refresh_delay**: How often the bot checks for new products (in seconds).
- **max_images_per_post**: The maximum number of images to display for each product.

## Troubleshooting

- If the bot fails to authenticate with the Vinted API, ensure that the `token` in `config.json` is correct and that Vinted's API is accessible.
- If you encounter errors while running the bot, check the `vinted_monitor.log` for more detailed error messages.
