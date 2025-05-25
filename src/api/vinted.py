from typing import List, Dict, Optional
import requests
from api.auth import Authenticator
from utils.logger import logger


class VintedAPI(Authenticator):
    def get_cookies(self) -> dict:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': 'vinted-ios Vinted/25.20.1 (iOS)',
            'X-Device-UUID': self.device_uuid,
        }
        response = requests.get("https://www.vinted.fr/api/v2/system_configuration", headers=headers)
        response.raise_for_status()
        return response.cookies.get_dict()

    async def search_products(self, search_text: str) -> List[Dict]:
        try:
            cookies = self.get_cookies()
            headers = {
                'Authorization': f'Bearer {self.token}',
                'User-Agent': 'vinted-ios Vinted/25.20.1 (iOS)',
                'X-Device-UUID': self.device_uuid,
            }
            params = {
                'search_text': search_text,
                'order': 'newest_first',
                'per_page': '24',
                'page': '1'
            }
            response = requests.get('https://www.vinted.fr/api/v2/catalog/items', headers=headers, cookies=cookies, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            return []

    async def get_product_details(self, product_id: str) -> Optional[Dict]:
        try:
            cookies = self.get_cookies()
            headers = {
                'Authorization': f'Bearer {self.token}',
                'User-Agent': 'vinted-ios Vinted/25.20.1 (iOS)',
                'X-Device-UUID': self.device_uuid,
            }
            response = requests.get(f'https://www.vinted.fr/api/v2/items/{product_id}/details', headers=headers, cookies=cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get product details: {str(e)}")
            return None