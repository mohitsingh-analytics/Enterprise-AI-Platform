from anthropic import Anthropic
class EvaluationService:
    def __init__(self, settings):
        self.settings = settings
        self.client = Anthropic(
            api_key=settings.anthropic_api_key
        )
    
    def evaluate(self, faithfulness, latency, cost):
        if (
            faithfulness >= 0.90
            and latency < 2
            and cost < 0.10
             ):
            return "Production Ready"

        return "Needs Improvement"