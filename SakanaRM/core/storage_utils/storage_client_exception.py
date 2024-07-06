class StorageClientException(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"CDN Error: {self.message}. Please try again later or contact the administrator for help"
