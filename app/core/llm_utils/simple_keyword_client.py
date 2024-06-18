from .abstract_llm_client import AbstractLLMClient
from .utils import read_pdf_texts


class SimpleKeywordClient(AbstractLLMClient):

    def match_paper_on_tags(self, file_obj, tags):
        with file_obj:
            pdf_texts = read_pdf_texts(file_obj)
        matching_tags = []
        for t in tags:
            if t in pdf_texts:
                matching_tags.append(t)
        return matching_tags
