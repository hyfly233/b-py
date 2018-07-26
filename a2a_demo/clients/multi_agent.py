import json
from typing import List

from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext

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

    def root_instruction(self, context: ReadonlyContext) -> str:
        current_agent = self.check_state(context)
        return f"""You are a expert delegator that can delegate the user request to the
        appropriate remote agents.
        
        Discovery:
        - You can use `list_remote_agents` to list the available remote agents you
        can use to delegate the task.
        
        Execution:
        - For actionable tasks, you can use `create_task` to assign tasks to remote agents to perform.
        Be sure to include the remote agent name when you respond to the user.
        
        You can use `check_pending_task_states` to check the states of the pending
        tasks.
        
        Please rely on tools to address the request, don't make up the response. If you are not sure, please ask the user for more details.
        Focus on the most recent parts of the conversation primarily.
        
        If there is an active agent, send the request to that agent with the update task tool.
        
        Agents:
        {self.agents}
        
        Current agent: {current_agent['active_agent']}
        """
