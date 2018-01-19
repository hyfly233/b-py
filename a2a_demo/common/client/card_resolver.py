import json

import httpx

from a2a_demo.common.types import AgentCard, A2AClientJSONError


class A2ACardResolver:
    def __init__(self, base_url, agent_card_path="/.well-known/agent.json"):
        self.base_url = base_url.rstrip("/")
        # 确保代理卡路径格式正确
        self.agent_card_path = agent_card_path.lstrip("/")

    def get_agent_card(self) -> AgentCard:
        """
        从指定的基本 URL 获取 AgentCard
        :return: AgentCard
        """
        with httpx.Client() as client:
            response = client.get(self.base_url + "/" + self.agent_card_path)
            # 检查响应状态代码是否指示错误
            response.raise_for_status()
            try:
                # 尝试将 JSON 响应解析为 AgentCard 对象
                return AgentCard(**response.json())
            except json.JSONDecodeError as e:
                # 如果 JSON 解析失败，则引发带有消息的自定义错误
                raise A2AClientJSONError(str(e)) from e
