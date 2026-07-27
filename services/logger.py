from anthropic import Anthropic
import logging

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Enterprise AI")

class LoggerService:
    def __init__(self, settings):
        self.settings = settings
        self.client = Anthropic(
            api_key=settings.anthropic_api_key
        )   
        

    def log_query(self, query):
        logger.info("Logging Query:", query)
    def log_env_details(self):
        logger.info("Logging mode details")
        print(self.settings.model_name)
 
# Git staging demo