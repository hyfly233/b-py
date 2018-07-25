import json
from typing import List

from google.adk import Agent

from a2a_demo.common.client import A2ACardResolver
from a2a_demo.common.types import AgentCard


class HostAgent:
    """
    主机代理。该代理负责选择要向其发送任务的远程代理，并协调其工作。
    """

    def __init__(
            self,
            remote_agent_addresses: List[str],
            task_callback: TaskUpdateCallback | None = None
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        for address in remote_agent_addresses:
            card_resolver = A2ACardResolver(address)
            card = card_resolver.get_agent_card()
            remote_connection = RemoteAgentConnections(card)
            self.remote_agent_connections[card.name] = remote_connection
            self.cards[card.name] = card
        agent_info = []
        for ra in self.list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = '\n'.join(agent_info)

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConnections(card)
        self.remote_agent_connections[card.name] = remote_connection
        self.cards[card.name] = card
        agent_info = []
        for ra in self.list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = '\n'.join(agent_info)

    def create_agent(self) -> Agent:
        # todo ollama
        return Agent(
            model="gemini-2.0-flash-001",
            name="host_agent",
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                "This agent orchestrates the decomposition of the user request into"
                " tasks that can be performed by the child agents."
            ),
            tools=[
                self.list_remote_agents,
                self.send_task,
            ],
        )
