import math
import time

from g4f.client import Client

from core.config import GPTClientConfig
from .abstract_llm_client import AbstractLLMClient
from .llm_client_exception import LLMClientException
from .utils import read_pdf_texts


class GPTClient(AbstractLLMClient):

    PAPER_SLICE_LENGTH = GPTClientConfig.PAPER_SLICE_LENGTH
    MODEL = GPTClientConfig.MODEL
    TEMPERATURE = GPTClientConfig.TEMPERATURE

    def match_paper_on_tags(self, paper, tags):
        if not tags:  # By default, return matching tags as an empty list if no tags to process
            return []
        try:
            content = read_pdf_texts(paper)
            slice_length = self.PAPER_SLICE_LENGTH
            num_slices = math.ceil(len(content) / slice_length)
            slices = [content[slice_length * i:slice_length * (i + 1)] for i in range(num_slices)]
            matching_tags = []

            messages = []
            init_query = f'Please read the following research paper content first and prepare to answer some ' \
                         f'questions based on the it. Part 1:{slices[0]}'
            messages.append({"role": "user", "content": init_query})
            messages.append({"role": "assistant", "content": "Please continue."})
            for i, s in enumerate(slices[1:]):
                query = f'Part {i + 2}: {s}'
                messages.append({"role": "user", "content": query})
                messages.append({"role": "assistant", "content": "Please continue."})
            # Note that "tags" is a dictionary
            tag_names = [n for n in tags.keys()]
            questions = [d for d in tags.values()]
            init_tag_query = f'Above is the full paper. Please ignore any links in it. ' \
                             f'Now please answer the following questions. Only respond with "yes" or "no". ' \
                             f'Question 1: {questions[0]}'
            messages.append({"role": "user", "content": init_tag_query})

            client = Client()

            response = client.chat.completions.create(model=self.MODEL, messages=messages, temperature=self.TEMPERATURE)
            choice = response.choices[0].message.content
            if 'yes' in choice.lower():
                matching_tags.append(tag_names[0])
            messages.append({"role": "assistant", "content": choice})

            for i, (n, d) in enumerate(zip(tag_names[1:], questions[1:])):
                time.sleep(1)  # avoid too frequent requests to API
                tag_query = f'Question 2: {d}'
                messages.append({"role": "user", "content": tag_query})
                response = client.chat.completions.create(model=self.MODEL, messages=messages,
                                                          temperature=self.TEMPERATURE)
                choice = response.choices[0].message.content
                if 'yes' in choice.lower():
                    matching_tags.append(n)
                messages.append({"role": "assistant", "content": choice})
            return matching_tags
        except Exception as e:
            # raise error and catch in core/views.py
            raise LLMClientException(str(e))
