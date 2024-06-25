from abc import ABC, abstractmethod
from typing import IO, List, Dict


class AbstractLLMClient(ABC):

    @abstractmethod
    def match_paper_on_tags(self, paper: IO, tags: Dict[str, str]):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

