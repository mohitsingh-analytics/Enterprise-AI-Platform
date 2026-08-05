from exceptions.exceptions import DocumentNotFoundException
from exceptions.exceptions import ValidationException
from services.logger import logger



class DocumentLoader:
    def load(self,file_name):
        if file_name == "":
             raise ValidationException(
            "Document name cannot be empty."
             )
    #    if file_not_exist:
    #        raise DocumentNotFoundException(file_name)
        logger.info(f"Loading file_name: {file_name}")
        return "this is sample document text"

    