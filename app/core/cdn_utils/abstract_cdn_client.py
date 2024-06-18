from abc import ABC, abstractmethod


class AbstractCDNClient(ABC):

    @abstractmethod
    def store_paper(self, paper):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

    @abstractmethod
    def request_for_paper(self, filepath):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

    @abstractmethod
    def delete_paper(self, filepath):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

    @abstractmethod
    def replace_paper(self, filepath, paper):
        """
        Request to replace full content of a paper. Method is PUT.
        :param filepath: path to old paper
        :param paper: file descriptor for new paper
        :return: status code 0 if successful otherwise 1
        """
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")
