from typing import Callable

from a2a_demo.common.types import Task, TaskStatusUpdateEvent, TaskArtifactUpdateEvent, AgentCard

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]

class RemoteAgentConnections:
    """
    用于保存与远程代理的连接的类
    """