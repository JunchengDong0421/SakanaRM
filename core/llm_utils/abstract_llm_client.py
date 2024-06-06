from abc import ABC, abstractmethod
from typing import TextIO, List


class AbstractLLMClient(ABC):

    @abstractmethod
    def match_paper_on_tags(self, paper: TextIO, tags: List):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

