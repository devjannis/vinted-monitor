import json
from dataclasses import dataclass
from typing import List
from utils.logger import logger


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
            with open(path) as f:
                return cls(**json.load(f))
        except FileNotFoundError:
            logger.warning("Config not found, using default values")
            return cls(token=None, channel_id=0, search_terms=["ralph lauren"])
