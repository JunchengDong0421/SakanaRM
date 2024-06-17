from requests_html import AsyncHTMLSession

from .abstract_cdn_client import AbstractCDNClient
from .config import CDNConfigDev
from .utils import random_filename


class SakanaCDNClient(AbstractCDNClient):
    __instance = None
    config = CDNConfigDev
    session = AsyncHTMLSession()

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    async def store_paper(self, fd):
        with fd:
            filename = random_filename()
            url = f"{self.config.CDN_HOST}{self.config.RESOURCE_REQUEST_PATH}{filename}"
            files = {"file": (filename, fd)}
            res = await self.session.post(url, files=files)

        filepath = res.json()['filepath']
        return filepath

    async def request_for_paper(self, *args, **kwargs):
        pass

    async def delete_paper(self, *args, **kwargs):
        pass

    async def replace_paper(self, filepath, paper):
        pass


if __name__ == '__main__':
    import asyncio

    async def main():
        my_client = SakanaCDNClient()

        file = open("C:\\Users\\Administrator\\Desktop\\project\\fd_production_suite_ICPADS23.pdf", "rb")
        task = loop.create_task(my_client.store_paper(file))
        result = await asyncio.gather(task)
        print(result)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
