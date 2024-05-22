from abc import ABC, abstractmethod


class AbstractCDNClient(ABC):

    @abstractmethod
    def store_paper(self, *args, **kwargs):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

    @abstractmethod
    def request_for_paper(self, *args, **kwargs):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

    @abstractmethod
    def delete_paper(self, *args, **kwargs):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")
