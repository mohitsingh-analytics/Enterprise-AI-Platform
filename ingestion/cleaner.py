from services.logger import logger

class Cleaner:
    def clean(self,text):
        logger.info("Cleaning Text")
        return text.strip()
    