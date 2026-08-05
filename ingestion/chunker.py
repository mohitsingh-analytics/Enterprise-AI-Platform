from services.logger import logger
class Chunker:

    def chunk(self, text):

        logger.info(f"created {len(text[:20])} chunks")

        return [
            text[:20],
            text[20:]
        ]