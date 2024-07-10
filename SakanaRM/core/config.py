# views: threshold of the number of parallel pending workflows
PENDING_WORKFLOWS_LIMIT = 5


# LLMClient configuration
class LLMClientConfig:
    # set default config if necessary
    pass


class GPTClientConfig(LLMClientConfig):
    PAPER_SLICE_LENGTH = 4000
    MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.1


# StorageClient configuration
class StorageClientConfig:
    # set default config if necessary
    pass


class SakanaStorageClientConfig(StorageClientConfig):
    BASE_URL = "http://192.168.196.130:5000/files/"
