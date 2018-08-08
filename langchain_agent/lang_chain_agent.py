from typing import List, Iterator

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_ollama import OllamaLLM


class StreamingCallback(BaseCallbackHandler):
    """自定义流式输出回调处理器"""

    def __init__(self):
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs):
        """当 LLM 生成新 token 时调用"""
        self.text += token
        yield token

class OllamaLangChainAgent:
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        初始化基于 LangChain 的 Ollama Agent，使用 ReAct 模式

        Args:
            model_name (str): Ollama 中加载的模型名称
            base_url (str): Ollama 服务器地址
        """
        self.model_name = model_name
        self.base_url = base_url

        # 初始化 OllamaLLM
        self.llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.7
        )

        # 初始化工具列表
        self.tools = []

        # 初始化对话历史
        self.chat_history = []

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
        self.tools.extend(tools)
        self._build_agent()

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        self._build_agent()

    def _build_agent(self):
        # 为 ReAct 格式创建提示模板
        react_template = f"""
{self.system_prompt}

你有权访问以下工具:
{{tools}}

使用以下格式回答:

Question: 用户的输入问题
Thought: 你对问题的思考过程
Action: 工具名称，必须是[{{tool_names}}]中的一个
Action Input: 提供给工具的输入
Observation: 工具的结果
... (可以有多个 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Answer: 对原始输入的回答

如果你不需要使用工具，可以直接回答用户的问题。

历史对话:
{{chat_history}}

Question: {{input}}
{{agent_scratchpad}}
"""
        prompt = ChatPromptTemplate.from_template(react_template)

        # 创建 ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 创建 Agent 执行器
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True
        )

        # 创建直接聊天提示
        self.chat_template = f"""
{self.system_prompt}

如果问题简单，可以直接回答。
如果需要使用工具，请明确告知用户你需要使用工具来回答这个问题。

历史对话:
{{chat_history}}

Question: {{input}}
"""
        self.chat_prompt = ChatPromptTemplate.from_template(self.chat_template)

    def query(self, user_input: str) -> str:
        """向 Agent 发送查询并获取回复"""
        try:
            # 准备历史对话文本
            chat_history_text = ""
            for i in range(0, len(self.chat_history), 2):
                if i + 1 < len(self.chat_history):
                    chat_history_text += f"Human: {self.chat_history[i].content}\n"
                    chat_history_text += f"AI: {self.chat_history[i + 1].content}\n"

            # 执行查询
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history_text
            })

            output = result.get("output", "出现了问题，未能获取回复")

            # 更新对话历史
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=output))

            return output
        except Exception as e:
            return f"执行过程中出错: {str(e)}"

    def query_stream(self, user_input: str) -> Iterator[str]:
        """流式查询，返回生成器对象逐步输出回复"""
        # 首先判断是否可能需要工具调用
        # 这是简化版本，假设以下关键词可能触发工具调用
        tool_keywords = [tool.name.lower() for tool in self.tools]
        tool_keywords.extend([d.split()[0].lower() for tool in self.tools for d in tool.description.split(',')])
        may_need_tool = any(keyword in user_input.lower() for keyword in tool_keywords)

        try:
            # 准备历史对话文本
            chat_history_text = self._format_chat_history()

            if may_need_tool:
                # 如果可能需要工具，使用普通非流式模式
                result = self.agent_executor.invoke({
                    "input": user_input,
                    "chat_history": chat_history_text
                }, stream=True)

                output = result.get("output", "出现了问题，未能获取回复")

                # 更新对话历史
                self.chat_history.append(HumanMessage(content=user_input))
                self.chat_history.append(AIMessage(content=output))

                # 一次性返回完整结果
                yield output
            else:
                # 如果可能不需要工具，使用流式输出
                # 创建自定义流式处理器
                streaming_handler = StreamingCallback()

                # 准备流式 LLM 实例
                llm_with_streaming = self.llm.with_config(
                    callbacks=[streaming_handler]
                )

                # 使用流式 LLM 直接回答
                chain = self.chat_prompt | llm_with_streaming

                # 收集流式输出的完整文本
                full_response = ""

                # 流式生成响应
                for chunk in chain.stream({
                    "input": user_input,
                    "chat_history": chat_history_text
                }):
                    full_response += chunk
                    yield chunk

                # 更新对话历史
                self.chat_history.append(HumanMessage(content=user_input))
                self.chat_history.append(AIMessage(content=full_response))

        except Exception as e:
            error_msg = f"执行过程中出错: {str(e)}"
            print(error_msg)
            yield error_msg

    def _format_chat_history(self) -> str:
        """格式化对话历史为文本"""
        chat_history_text = ""
        for i in range(0, len(self.chat_history), 2):
            if i + 1 < len(self.chat_history):
                chat_history_text += f"Human: {self.chat_history[i].content}\n"
                chat_history_text += f"AI: {self.chat_history[i + 1].content}\n"
        return chat_history_text

    def reset_memory(self):
        """重置对话历史"""
        self.chat_history = []

    def get_history(self):
        """获取对话历史"""
        return self.chat_history


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

    # 交互式聊天
    print("AI Agent 已准备好。输入 'exit' 退出。")

    # 普通查询
    # while True:
    #     user_input = input("\n用户: ")
    #     if user_input.lower() == 'exit':
    #         break
    #
    #     response = agent.query(user_input)
    #     print(f"\nAI: {response}")

    # 流式查询示例
    while True:
        user_input = input("\n用户: ")
        if user_input.lower() == 'exit':
            break

        print("\nAI: ", end="", flush=True)
        # 使用流式输出
        for chunk in agent.query_stream(user_input):
            print(chunk, end="", flush=True)
        print()
