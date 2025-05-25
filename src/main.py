# main.py
from models.config import VintedConfig
from discord_utils.bot import VintedMonitor


def main():
    try:
        config = VintedConfig.load()
        client = VintedMonitor(config)
        client.run(config.token)
    except Exception as e:
        from utils.logger import logger
        logger.critical(f"Failed to start the bot: {str(e)}")


if __name__ == "__main__":
    main()