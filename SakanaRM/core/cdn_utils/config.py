from django.conf import settings


class BaseCDNConfig:
    RESOURCE_REQUEST_PATH = "/files/"


class CDNConfigDev(BaseCDNConfig):
    CDN_HOST = "http://localhost:5000"


class CDNConfigProd(BaseCDNConfig):
    CDN_HOST = "http://10.105.6.24:5000"


def get_cdn_config():
    env = settings.CDN_CLIENT_ENV
    if env == "dev":
        return CDNConfigDev
    return CDNConfigProd


__all__ = [
    get_cdn_config,
]
