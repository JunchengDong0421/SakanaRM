import asyncio

from requests_html import AsyncHTMLSession

from .abstract_cdn_client import AbstractCDNClient


class SakanaCDNClient(AbstractCDNClient):

    __instance = None
    session = AsyncHTMLSession()

    async def request_store(self, url):
        res = await self.session.get(url)
        return res.content

    def run(self):
        loop = asyncio.get_running_loop()

    def store_paper(self, *args, **kwargs):
        pass
