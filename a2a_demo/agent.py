from typing import List, Dict, Any

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
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

        # 构建 Agent (初始时没有工具)
        self._build_agent()

    def add_tool(self, tool: Tool):
        """添加工具到 Agent"""
        self.tools.append(tool)
        # 重新构建 Agent 以包含新工具
        self._build_agent()

    def add_tools(self, tools: List[Tool]):
        """添加多个工具到 Agent"""
        self.tools.extend(tools)
        # 重新构建 Agent 以包含新工具
        self._build_agent()

    def set_system_prompt(self, prompt: str):
        """设置系统提示"""
        self.system_prompt = prompt
        # 重新构建带有新系统提示的 Agent
        self._build_agent()

    def _build_agent(self):
        """构建 Agent 执行器"""
        # 创建 Agent 提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # 创建基于函数的 Agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 创建 Agent 执行器
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=False,
            handle_parsing_errors=True
        )

    def query(self, user_input: str) -> str:
        """向 Agent 发送查询并获取回复"""
        try:
            result = self.agent_executor.invoke({"input": user_input})
            return result.get("output", "出现了问题，未能获取回复")
        except Exception as e:
            return f"执行过程中出错: {str(e)}"

    def reset_memory(self):
        """重置对话历史"""
        self.memory.clear()

    def get_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.memory.chat_memory.messages
