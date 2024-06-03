from PyPDF2 import PdfReader

from .abstract_llm_client import AbstractLLMClient


class SimpleKeywordClient(AbstractLLMClient):

    def read_pdf_content(self, file_obj):
        reader = PdfReader(file_obj)
        # Check if the PDF is encrypted
        if reader.is_encrypted:
            reader.decrypt('')

        text_content = []
        # Iterate through all the pages
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text_content.append(page.extract_text())

        return " ".join(text_content)

    async def process_paper_on_tags(self, file_obj, tags):
        with file_obj as f:
            file_content = f.read()
        matching_tags = []
        for t in tags:
            if t in file_content:
                matching_tags.append(t)
        return matching_tags
