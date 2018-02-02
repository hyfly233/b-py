from langchain_ollama import Ollama

class OllamaLangChainAgent:
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

        # 初始化 Ollama LLM
        self.llm = Ollama(

        )
