import aiohttp
from core.config import SUPERCELL_API_KEY

async def fetch_player_data(tag: str):
    clean_tag = tag.replace("#", "").upper()
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {SUPERCELL_API_KEY}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return None, clean_tag
            return await response.json(), clean_tag