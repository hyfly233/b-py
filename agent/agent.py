import json
import re
from typing import Dict, List, Optional, Callable

import requests

MODEL_NAME = "qwen2.5-coder:7b"


class OllamaAgent:
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        初始化 Ollama Agent

        Args:
            model_name (str): Ollama 中加载的模型名称
            base_url (str): Ollama 服务器地址
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.history: List[Dict[str, str]] = []

    def query(self, prompt: str, system_prompt: Optional[str] = None,
              temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        向 Ollama 模型发送查询

        Args:
            prompt (str): 用户输入的提示
            system_prompt (str, optional): 系统提示
            temperature (float): 温度参数，控制输出的随机性
            max_tokens (int): 生成的最大 token 数量

        Returns:
            str: 模型的回复
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            result = response.json()

            # 记录对话历史
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": result["response"]})

            return result["response"]
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"

    def chat(self, messages: List[Dict[str, str]],
             temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        使用 chat API 与模型对话

        Args:
            messages (List[Dict]): 对话历史消息列表
            temperature (float): 温度参数
            max_tokens (int): 最大 token 数

        Returns:
            str: 模型回复
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()

            return result["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"

    def list_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            result = response.json()
            return [model["name"] for model in result["models"]]
        except requests.exceptions.RequestException as e:
            print(f"Error listing models: {str(e)}")
            return []


class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func


class OllamaAgentWithTools:
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.history: List[Dict[str, str]] = []
        self.tools: List[Tool] = []

    def add_tool(self, tool: Tool):
        """添加工具到 Agent"""
        self.tools.append(tool)

    def get_tools_description(self) -> str:
        """获取工具描述文本"""
        if not self.tools:
            return ""

        desc = "你可以使用以下工具来帮助回答问题:\n\n"
        for tool in self.tools:
            desc += f"- {tool.name}: {tool.description}\n"

        desc += "\n使用工具时，请使用以下格式：\n"
        desc += "```\n思考: 我需要使用工具来解决这个问题\n工具: [工具名称]\n工具输入: [工具需要的输入]\n```\n"
        return desc

    def query_with_tools(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """使用工具功能发送查询"""
        tools_desc = self.get_tools_description()

        # 合并系统提示和工具描述
        if system_prompt:
            full_system_prompt = f"{system_prompt}\n\n{tools_desc}"
        else:
            full_system_prompt = tools_desc if tools_desc else None

        # 第一次查询，获取模型回复
        response = self.query(prompt, full_system_prompt)

        # 检查回复中是否使用了工具
        tool_usage = self._extract_tool_usage(response)

        # 如果使用了工具，执行工具并将结果添加到查询中
        if tool_usage:
            tool_name = tool_usage["tool"]
            tool_input = tool_usage["input"]

            # 查找并执行工具
            tool_result = "工具不可用"
            for tool in self.tools:
                if tool.name == tool_name:
                    try:
                        tool_result = tool.func(tool_input)
                    except Exception as e:
                        tool_result = f"工具执行错误: {str(e)}"
                    break

            # 构建带有工具结果的新查询
            new_prompt = f"{prompt}\n\n工具执行结果:\n{tool_result}\n\n请根据工具结果回答我的问题。"

            # 再次查询模型
            return self.query(new_prompt, full_system_prompt)

        return response

    def _extract_tool_usage(self, text: str) -> Optional[Dict[str, str]]:
        """从回复中提取工具使用信息"""
        # 使用正则表达式匹配工具使用模式
        pattern = r"工具: *([\w\d_-]+)\s*\n工具输入: *(.*?)(?:\n```|\Z)"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            return {
                "tool": match.group(1).strip(),
                "input": match.group(2).strip()
            }
        return None

    def query(self, prompt: str, system_prompt: Optional[str] = None,
              temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """基本查询实现"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            result = response.json()

            # 记录对话历史
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": result["response"]})

            return result["response"]
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"

    def query_stream(self, prompt: str, system_prompt: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 2048):
        """使用流式响应发送查询"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.api_url, json=payload, stream=True)
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    chunk_text = chunk.get('response', '')
                    full_response += chunk_text
                    yield chunk_text

                    if chunk.get('done', False):
                        break

            # 记录对话历史
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": full_response})
        except requests.exceptions.RequestException as e:
            yield f"Error communicating with Ollama: {str(e)}"


# 示例用法
if __name__ == "__main__":
    # 定义一些工具函数
    def get_weather(location: str) -> str:
        # 这里应该是实际的天气 API 调用
        return f"{location}的天气：晴天，25°C"


    def calculate(expression: str) -> str:
        try:
            return f"计算结果: {eval(expression)}"
        except Exception as e:
            return f"计算错误: {str(e)}"


    # 创建带有工具的 Agent
    agent = OllamaAgentWithTools(model_name=MODEL_NAME)

    # 添加工具
    agent.add_tool(Tool("weather", "获取指定地区的天气信息", get_weather))
    agent.add_tool(Tool("calculator", "计算数学表达式", calculate))

    # 带有工具的交互式聊天
    print("AI Agent 已准备好。输入 'exit' 退出。")

    while True:
        user_input = input("\n用户: ")
        if user_input.lower() == 'exit':
            break

        # 一次性输出
        response = agent.query_with_tools(user_input)
        print(f"\nAI: {response}")

        # 流式输出示例
        # print("\nAI: ", end="", flush=True)
        # for text_chunk in agent.query_stream(user_input):
        #     print(text_chunk, end="", flush=True)
        # print()
