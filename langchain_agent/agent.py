from typing import List, Dict, Any, Iterator

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
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
        functions_agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 创建 Agent 执行器
        self.agent_executor = AgentExecutor(
            agent=functions_agent,
            tools=self.tools,
            # memory=self.memory,
            verbose=False,
            handle_parsing_errors=True
        )

        # # 构建直接响应的链
        self.chat_chain = (
                ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}")
                ])
                | self.llm
                | StrOutputParser()
        )


    def query(self, user_input: str) -> str:
        """向 Agent 发送查询并获取回复"""
        try:
            result = self.agent_executor.invoke({"input": user_input})
            return result.get("output", "出现了问题，未能获取回复")
        except Exception as e:
            return f"执行过程中出错: {str(e)}"

    def query_stream(self, user_input: str) -> Iterator[str]:
        """流式查询，返回生成器对象"""
        try:
            # 先检查是否有工具需要调用
            has_tools = any(tool_name.lower() in user_input.lower() for tool in self.tools for tool_name in
                            [tool.name, tool.description.split()[0]])

            # 如果明显需要工具调用，使用非流式 agent
            if has_tools:
                result = self.agent_executor.invoke({"input": user_input}, stream=True)
                yield result.get("output", "出现了问题，未能获取回复")
            else:
                # 否则尝试使用流式响应
                chat_history = self.memory.load_memory_variables({})["chat_history"]

                for chunk in self.chat_chain.stream({
                    "input": user_input,
                    "chat_history": chat_history
                }):
                    yield chunk

                # 更新记忆
                self.memory.save_context({"input": user_input}, {"output": "".join(
                    chunk for chunk in self.chat_chain.stream({"input": user_input, "chat_history": chat_history}))})

        except Exception as e:
            yield f"执行过程中出错: {str(e)}"

    def reset_memory(self):
        """重置对话历史"""
        self.memory.clear()

    def get_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.memory.chat_memory.messages


def get_weather(location: str) -> str:
    """根据位置获取天气信息"""
    # 这里应该调用真实的天气 API
    # 下面是模拟的返回结果
    return f"{location}的天气：晴天，25°C，湿度60%"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 使用安全的 eval 替代方案
        # 注意：在生产环境中不应直接使用 eval
        from ast import literal_eval
        import operator
        import math

        # 定义允许的操作
        safe_dict = {
            'abs': abs,
            'float': float,
            'int': int,
            'max': max,
            'min': min,
            'pow': pow,
            'round': round,
            'sum': sum,
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi,
            'e': math.e
        }

        # 替换常见的数学函数名称
        expression = expression.replace('sqrt', 'math.sqrt')
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        expression = expression.replace('pi', 'math.pi')

        # 使用 eval 计算表达式
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def search_web(query: str) -> str:
    """搜索网络获取信息"""
    # 这里应该调用真实的搜索 API，比如 Bing, Google 等
    # 下面是模拟的返回结果
    return f"关于 '{query}' 的搜索结果：\n1. 相关文章A\n2. 相关网页B\n3. 维基百科条目C"


# 使用示例
if __name__ == "__main__":
    # 创建 LangChain Agent
    agent = OllamaLangChainAgent(model_name="llama3")

    # 定义工具
    tools = [
        Tool(
            name="weather",
            description="获取指定地点的天气信息，输入应该是城市名或地区名",
            func=get_weather
        ),
        Tool(
            name="calculator",
            description="计算数学表达式，可以处理基本运算和一些高级函数如平方根(sqrt)、三角函数(sin,cos,tan)",
            func=calculate
        ),
        Tool(
            name="web_search",
            description="在网络上搜索信息，当需要最新信息或事实性知识时使用",
            func=search_web
        )
    ]

    # 添加工具
    agent.add_tools(tools)

    # 设置自定义系统提示
    agent.set_system_prompt("""你是一个智能助手，擅长解决各种问题。
当用户的问题可以通过工具解决时，请优先使用提供的工具。
回答应该简洁明了，信息丰富。如果你不确定答案，请诚实地说出来，不要猜测。
在使用计算工具时，请确保正确理解了用户的数学问题。
在获取天气信息时，请确保从用户输入中提取正确的位置信息。""")

    # 交互式聊天
    print("AI Agent 已准备好。输入 'exit' 退出。")

    # 普通查询
    while True:
        user_input = input("\n用户: ")
        if user_input.lower() == 'exit':
            break

        response = agent.query(user_input)
        print(f"\nAI: {response}")

    # 流式查询示例
    # while True:
    #     user_input = input("\n用户: ")
    #     if user_input.lower() == 'exit':
    #         break
    #
    #     print("\nAI: ", end="", flush=True)
    #     for chunk in agent.query_stream(user_input):
    #         print(chunk, end="", flush=True)
    #     print()
