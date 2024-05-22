from _io import BytesIO
import asyncio

from .abstract_cdn_client import AbstractCDNClient
from .http_session import make_store_request_to_cdn_server


class PseudoCDNClient(AbstractCDNClient):
    # singleton pattern
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    async def store_paper(self, file_obj):
        # Takes in a file, make a request to store it in cdn server and retrieve the filepath (url)
        # to access it. The logic is, by directly accessing this url, we will have access to the paper
        # "file_obj" is a file I/O object or in-memory buffer
        await asyncio.sleep(5)
        filepath = "random_path_1"
        # filepath = make_store_request_to_cdn_server(file_obj, replace)
        return filepath

    async def request_for_paper(self, filepath=None):
        file = BytesIO(b"Random content")
        return file

    async def delete_paper(self, filepath=None):
        status = 0
        return status
