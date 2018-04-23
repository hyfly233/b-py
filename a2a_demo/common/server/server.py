import logging

from a2a_demo.common.types import AgentCard

logger = logging.getLogger(__name__)


class A2AServer:
    def __init__(self, host="0.0.0.0", port=5000, endpoint="/", agent_card: AgentCard = None,
                 task_manager: TaskManager = None):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.task_manager = task_manager
        self.agent_card = agent_card
        self.app = Starlette()
        self.app.add_route(self.endpoint, self._process_request, methods=["POST"])
        self.app.add_route(
            "/.well-known/agent.json", self._get_agent_card, methods=["GET"]
        )
