from .abstract_llm_client import AbstractLLMClient


class PseudoLLMClient(AbstractLLMClient):

    async def generate_tags_for_paper(self, file_obj):
        import asyncio
        await asyncio.sleep(10)
        return ["dt_on_FD", "pa_on_FD", "md_on_FD"]

    async def query_for_tags(self, tags, file_obj):
        # tags = {tag.name: {"prompt": tag.definition} }
        pass
