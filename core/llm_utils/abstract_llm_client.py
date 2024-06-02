from abc import ABC


class AbstractLLMClient(ABC):

    def process_paper_on_tags(self, *args, **kwargs):
        raise NotImplementedError(f"Abstract method {self.__class__.__name__} not implemented!")

