from abc import ABC, abstractmethod
from typing import Union, AsyncIterable, List
import asyncio
import logging

from a2a_demo.common.types import GetTaskRequest, GetTaskResponse

logger = logging.getLogger(__name__)

class TaskManager(ABC):
    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        pass