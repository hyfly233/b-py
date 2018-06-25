import json
from typing import AsyncIterable

from typing import Union
import logging

from a2a_demo.agents.agent import TestOllamaAgent
from a2a_demo.common.server import InMemoryTaskManager

logger = logging.getLogger(__name__)

class AgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent: TestOllamaAgent):
        super().__init__()
        self.agent = agent