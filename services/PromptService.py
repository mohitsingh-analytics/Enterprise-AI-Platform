from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

class PromptService:
    """
    load the default prompt from prompts folder, and replace Context and Query with {context} and {Query}
    """
    prompt_files={
        "default": "default_prompt.txt",
        "strict": "strict_prompt.txt"
    }
    def __init__(self, prompt_dir: str ="prompts"):
        self.prompt_dir = Path(prompt_dir)
        self.template_cache= {}

    def read_prompt(self,prompt_name:str):
        if prompt_name in self.template_cache:
            return self.template_cache[prompt_name]

        if prompt_name not in self.prompt_files:
            raise FileNotFoundError
        
        prompt_path = self.prompt_dir / self.prompt_files[prompt_name]
        raw_text= prompt_path.read_text(encoding="utf-8") 
        raw_text_template =ChatPromptTemplate.from_template(raw_text)
        print("="*60, " raw temaple", raw_text_template)
        self.template_cache[prompt_name] = raw_text_template
        return raw_text_template
    
    def build_prompt(self, query: str, context: str, prompt_name: str = "default"):
        template= self.read_prompt(prompt_name)
        results = template.invoke( 
            {
            "context": context,
            "query": query
            }
        )
        return results.to_string()  