import math
import time

from g4f.Provider import You
from g4f.client import Client

from .abstract_llm_client import AbstractLLMClient
from .llm_client_exception import LLMClientException
from .utils import read_pdf_texts


class GPTClient(AbstractLLMClient):

    PAPER_SLICE_LENGTH = 4000
    MODEL_TEMPERATURE = 0.1

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

            client = Client(provider=You)

            temperature = self.MODEL_TEMPERATURE
            response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=temperature)
            choice = response.choices[0].message.content
            if 'yes' in choice.lower():
                matching_tags.append(tag_names[0])
            messages.append({"role": "assistant", "content": choice})

            for i, (n, d) in enumerate(zip(tag_names[1:], questions[1:])):
                time.sleep(1)  # avoid too frequent requests to API
                tag_query = f'Question 2: {d}'
                messages.append({"role": "user", "content": tag_query})
                response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages,
                                                          temperature=temperature)
                choice = response.choices[0].message.content
                if 'yes' in choice.lower():
                    matching_tags.append(n)
                messages.append({"role": "assistant", "content": choice})
            return matching_tags
        except Exception as e:
            # raise error and catch in core/views.py
            raise LLMClientException(str(e))


if __name__ == '__main__':
    my_client = GPTClient()
    paper_ = open("C:\\Users\\Administrator\\Desktop\\project\\fd_production_suite_ICPADS23.pdf", "rb")
    tags_ = {"dt_on_fd": "Does the paper applies the metric detection time to benchmark failure detectors?",
             "f1_on_fd": "Does the paper applies the metric F1 score to benchmark failure detectors?",
             "AI": "Does the paper mainly talks about AI or not?"}
    m_tags = my_client.match_paper_on_tags(paper_, tags_)
    print("Matching tags:", m_tags)
