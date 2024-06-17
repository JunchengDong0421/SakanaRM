class BaseCDNConfig:
    RESOURCE_REQUEST_PATH = "/files/"


class CDNConfigDev(BaseCDNConfig):
    CDN_HOST = "http://localhost:5000"


class CDNConfigProd(BaseCDNConfig):
    CDN_HOST = "http://cdn.sakanarm.com"


__all__ = [
    CDNConfigDev,
    CDNConfigProd,
]
