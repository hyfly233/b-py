from typing import Any, AsyncIterable, Dict, Iterator

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_ollama import OllamaLLM

from langchain_agent.lang_chain_agent import StreamingCallback

request_ids = set()


@tool
def tool_echo_hello_world() -> str:
    return "Java - Hello, World!"

class TestOllamaAgent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(
            self,
            model_name: str = "llama3",
            base_url: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.base_url = base_url

        self.llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.7
        )

        # todo
        self.tools = []

        # 构建 Agent (初始时没有工具)
        self._build_agent()


    def invoke(self, query, session_id) -> str:
        config: RunnableConfig = {"configurable": {"thread_id": session_id}}

        result = self.agent_executor.invoke(
            input={
                "input": query
            },
            config=config
        )

        output = result.get("output", "出现了问题，未能获取回复")
        return output

    async def stream(self, query, session_id) -> AsyncIterable[Dict[str, Any]]:
        pass

    def _build_agent(self):
        # 为 ReAct 格式创建提示模板
        react_template = f"""
test
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
test
历史对话:
{{chat_history}}

Question: {{input}}
"""
        self.chat_prompt = ChatPromptTemplate.from_template(self.chat_template)

    def query_stream(self, user_input: str) -> Iterator[str]:
        """流式查询，返回生成器对象逐步输出回复"""
        # 首先判断是否可能需要工具调用
        # 这是简化版本，假设以下关键词可能触发工具调用
        tool_keywords = [tool.name.lower() for tool in self.tools]
        tool_keywords.extend([d.split()[0].lower() for tool in self.tools for d in tool.description.split(',')])
        may_need_tool = any(keyword in user_input.lower() for keyword in tool_keywords)

        try:

            if may_need_tool:
                # 如果可能需要工具，使用普通非流式模式
                result = self.agent_executor.invoke({
                    "input": user_input,
                }, stream=True)

                output = result.get("output", "出现了问题，未能获取回复")

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
                }):
                    full_response += chunk
                    yield chunk

        except Exception as e:
            error_msg = f"执行过程中出错: {str(e)}"
            print(error_msg)
            yield error_msg
