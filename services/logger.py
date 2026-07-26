from anthropic import Anthropic
class LoggerService:
    def __init__(self, settings):
        self.settings = settings
        self.client = Anthropic(
            api_key=settings.anthropic_api_key
        )   
        

    def log_query(self, query):
        print(f"loggin query: {query}")
    def log_env_details(self):
        print(self.settings.model_name)
 
# Git staging demo