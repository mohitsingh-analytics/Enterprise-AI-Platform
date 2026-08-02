class DocumentNotFoundException(Exception):

    def __init__(self, document_name):

        self.document_name = document_name

        super().__init__(
            f"Document '{document_name}' not found."
        )

class ValidationException(Exception):

    def __init__(self, message):
        super().__init__(message)