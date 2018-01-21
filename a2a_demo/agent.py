from langchain.memory import ConversationBufferMemory
from langchain_ollama.llms import OllamaLLM

class OllamaLangChainAgent:
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

        # 初始化 Ollama LLM
        self.llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.7,
        )

        # 初始化工具列表
        self.tools = []

        # 初始化会话记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 默认的系统提示
        self.system_prompt = """你是一个有帮助的AI助手。当提供给你工具时，请优先考虑使用工具来回答问题。
        如果你不知道答案，请坦诚地说不知道，不要编造信息。回答问题要准确、有帮助、简洁。"""