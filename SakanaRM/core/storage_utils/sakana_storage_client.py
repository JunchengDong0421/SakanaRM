from io import BytesIO

import requests

from .abstract_storage_client import AbstractStorageClient
from .storage_client_exception import StorageClientException
from .utils import random_filename


class SakanaStorageClient(AbstractStorageClient):
    __instance = None
    BASE_URL = "http://192.168.196.130:5000/files/"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def store_paper(self, fd):
        try:
            with fd:
                filename = random_filename()
                url = f"{self.BASE_URL}{filename}"
                files = {"file": (filename, fd)}
                res = requests.post(url, files=files)
            json_res = res.json()
            if res.status_code != 201 or 'filepath' not in json_res:
                raise ValueError(json_res.get("error", "Something went wrong"))

            filepath = json_res['filepath']
            return filepath
        except Exception as e:
            # wrap, raise error and catch in core/views.py
            raise StorageClientException(str(e))

    def request_for_paper(self, filepath):
        try:
            res = requests.get(filepath)
            if res.status_code != 200:
                json_res = res.json()
                raise ValueError(json_res.get("error", "Something went wrong"))

            fd = BytesIO(res.content)
            return fd
        except Exception as e:
            raise StorageClientException(str(e))

    def delete_paper(self, filepath):
        try:
            res = requests.delete(filepath)
            json_res = res.json()
            if res.status_code != 200 or 'filepath' not in json_res:
                raise ValueError(json_res.get("error", "Something went wrong"))

            filepath = json_res['filepath']
            return filepath
        except Exception as e:
            raise StorageClientException(str(e))

    def replace_paper(self, filepath, new_fd):
        try:
            with new_fd:
                filename = random_filename()
                files = {"file": (filename, new_fd)}
                res = requests.put(filepath, files=files)
            json_res = res.json()
            if res.status_code != 200 or 'filepath' not in json_res:
                raise ValueError(json_res.get("error", "Something went wrong"))

            new_filepath = json_res['filepath']
            return new_filepath
        except Exception as e:
            raise StorageClientException(str(e))
