from io import BytesIO

import requests

from .abstract_cdn_client import AbstractCDNClient
from .cdn_client_exception import CDNClientException
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
        json_res = res.json()
        if res.status_code != 201 or 'filepath' not in json_res:
            # raise error and catch in core/views.py
            raise CDNClientException(json_res.get("error", "Something went wrong"))

        filepath = json_res['filepath']
        return filepath

    def request_for_paper(self, filepath):
        res = requests.get(filepath)
        if res.status_code != 200:
            json_res = res.json()
            raise CDNClientException(json_res.get("error", "Something went wrong"))

        fd = BytesIO(res.content)
        return fd

    def delete_paper(self, filepath):
        res = requests.delete(filepath)
        json_res = res.json()
        if res.status_code != 200 or 'filepath' not in json_res:
            raise CDNClientException(json_res.get("error", "Something went wrong"))

        filepath = json_res['filepath']
        return filepath

    def replace_paper(self, filepath, new_fd):
        with new_fd:
            filename = random_filename()
            files = {"file": (filename, new_fd)}
            res = requests.put(filepath, files=files)
        json_res = res.json()
        if res.status_code != 200 or 'filepath' not in json_res:
            raise CDNClientException(json_res.get("error", "Something went wrong"))

        new_filepath = json_res['filepath']
        return new_filepath
