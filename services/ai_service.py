
from anthropic import Anthropic
from dotenv import load_dotenv
from services import PromptService
import os

load_dotenv()

class AIService:
    def __init__(self, settings):
        self.settings = settings
        self.client = Anthropic(
            api_key=settings.anthropic_api_key
        )

    def ask_claude(self,query: str, context: str, history):
        
            # 2. Create your fresh, current message
        current_message = [{
            "role": "user",
            "content": query
        }]
        conv_history= [{
            "role": "user",
            "content": "conversation history"
        }]


        payload_messages = conv_history + history   + current_message
        print("&&&"*10,history)
        response = self.client.messages.create(
            model=self.settings.model_name,
            max_tokens=self.settings.max_tokens, 
            messages= payload_messages
            )

        return(response.content[0].text)


                

                