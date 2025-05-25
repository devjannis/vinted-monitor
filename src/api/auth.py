import uuid
import requests
from typing import Optional
from utils.logger import logger


class Authenticator:
    def __init__(self):
        self.device_uuid = self.generate_device_uuid()
        self.token: Optional[str] = None

    def generate_device_uuid(self):
        return uuid.uuid4().hex.lower()

    async def authenticate(self):
            headers = {
                'Host': 'www.vinted.fr',
                'Accept': '*/*',
                'Accept-Language': 'fr',
                'X-Device-UUID': self.device_uuid,
                'User-Agent': 'vinted-ios Vinted/25.20.1 (iOS)',
                'Short-Bundle-Version': '25.20.1',
                'X-Device-Model': 'iPhone15,4',
                'X-App-Version': '25.20.1',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
            }

            data = {
                'grant_type': 'password',
                'client_id': 'ios',
                'scope': 'public',
            }

            response = requests.post('https://www.vinted.fr/oauth/token', headers=headers, json=data)
            response.raise_for_status()
            self.token = response.json().get("access_token")
            return True