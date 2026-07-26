def evaluate_run(
        faithfulness,
        latency,
        cost):

    if (
        faithfulness >= 0.90
        and latency < 2
        and cost < 0.10
    ):
        return "Production Ready"

    return "Needs Improvement"

from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
def query_(query,userContext):
       
        client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": query + "for age" + userContext.Age + " " + "answer in yes/no"
                }
            ]
        )

        return(response.content[0].text)