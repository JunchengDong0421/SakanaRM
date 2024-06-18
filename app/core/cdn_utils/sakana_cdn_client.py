from io import BytesIO

import requests

from .abstract_cdn_client import AbstractCDNClient
from .config import CDNConfigDev
from .utils import random_filename


class SakanaCDNClient(AbstractCDNClient):
    __instance = None
    config = CDNConfigDev

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def store_paper(self, fd):
        with fd:
            filename = random_filename()
            url = f"{self.config.CDN_HOST}{self.config.RESOURCE_REQUEST_PATH}{filename}"
            files = {"file": (filename, fd)}
            res = requests.post(url, files=files)

        filepath = res.json()['filepath']
        return filepath

    def request_for_paper(self, filepath):
        res = requests.get(filepath)
        fd = BytesIO(res.content)
        return fd

    def delete_paper(self, filepath):
        _ = requests.delete(filepath)
        return filepath

    def replace_paper(self, filepath, new_fd):
        with new_fd:
            filename = random_filename()
            files = {"file": (filename, new_fd)}
            res = requests.put(filepath, files=files)

        new_filepath = res.json()['filepath']
        return new_filepath
