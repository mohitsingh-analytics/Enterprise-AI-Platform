from services.logger import logger
class MetadataBuilder:

    def build(self, chunks):
        logger.info("Building metadata successfully")

        result = []
        for i, _ in enumerate(chunks):
            result.append({
                "chunk_id": i,
                "source": "LeavePolicy.pdf"
            })
        return result