import json
import random
from typing import Any, AsyncIterable, Dict, Optional

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

request_ids = set()


def create_request_form(date: Optional[str] = None, amount: Optional[str] = None, purpose: Optional[str] = None) -> \
dict[str, Any]:
    """
     Create a request form for the employee to fill out.

     Args:
         date (str): The date of the request. Can be an empty string.
         amount (str): The requested amount. Can be an empty string.
         purpose (str): The purpose of the request. Can be an empty string.

     Returns:
         dict[str, Any]: A dictionary containing the request form data.
     """
    request_id = "request_id_" + str(random.randint(1000000, 9999999))
    request_ids.add(request_id)
    return {
        "request_id": request_id,
        "date": "<transaction date>" if not date else date,
        "amount": "<transaction dollar amount>" if not amount else amount,
        "purpose": "<business justification/purpose of the transaction>" if not purpose else purpose,
    }


def return_form(
        form_request: dict[str, Any],
        tool_context: ToolContext,
        instructions: Optional[str] = None) -> dict[str, Any]:
    """
     Returns a structured json object indicating a form to complete.

     Args:
         form_request (dict[str, Any]): The request form data.
         tool_context (ToolContext): The context in which the tool operates.
         instructions (str): Instructions for processing the form. Can be an empty string.

     Returns:
         dict[str, Any]: A JSON dictionary for the form response.
     """
    if isinstance(form_request, str):
        form_request = json.loads(form_request)

    tool_context.actions.skip_summarization = True
    tool_context.actions.escalate = True
    form_dict = {
        'type': 'form',
        'form': {
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Date of expense',
                    'title': 'Date',
                },
                'amount': {
                    'type': 'string',
                    'format': 'number',
                    'description': 'Amount of expense',
                    'title': 'Amount',
                },
                'purpose': {
                    'type': 'string',
                    'description': 'Purpose of expense',
                    'title': 'Purpose',
                },
                'request_id': {
                    'type': 'string',
                    'description': 'Request id',
                    'title': 'Request ID',
                },
            },
            'required': list(form_request.keys()),
        },
        'form_data': form_request,
        'instructions': instructions,
    }
    return json.dumps(form_dict)


def reimburse(request_id: str) -> dict[str, Any]:
  """Reimburse the amount of money to the employee for a given request_id."""
  if request_id not in request_ids:
    return {"request_id": request_id, "status": "Error: Invalid request_id."}
  return {"request_id": request_id, "status": "approved"}

class Test01Agent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = "remote_agent"
        self._runner = Runner(
        app_name=self._agent.name,
        agent=self._agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
