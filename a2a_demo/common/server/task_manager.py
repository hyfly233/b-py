import logging
from abc import ABC, abstractmethod
from typing import Union, AsyncIterable

from a2a_demo.common.types import GetTaskRequest, GetTaskResponse, CancelTaskRequest, CancelTaskResponse, \
    SendTaskRequest, SendTaskResponse, SendTaskStreamingRequest, SendTaskStreamingResponse, JSONRPCResponse, \
    SetTaskPushNotificationRequest, SetTaskPushNotificationResponse, GetTaskPushNotificationRequest, \
    GetTaskPushNotificationResponse, TaskResubscriptionRequest

logger = logging.getLogger(__name__)

class TaskManager(ABC):
    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        pass

    @abstractmethod
    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        pass

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        pass

    @abstractmethod
    async def on_send_task_subscribe(
            self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        pass

    @abstractmethod
    async def on_set_task_push_notification(
            self, request: SetTaskPushNotificationRequest
    ) -> SetTaskPushNotificationResponse:
        pass

    @abstractmethod
    async def on_get_task_push_notification(
            self, request: GetTaskPushNotificationRequest
    ) -> GetTaskPushNotificationResponse:
        pass

    @abstractmethod
    async def on_resubscribe_to_task(
            self, request: TaskResubscriptionRequest
    ) -> Union[AsyncIterable[SendTaskResponse], JSONRPCResponse]:
        pass
