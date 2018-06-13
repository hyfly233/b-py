import json
import random
from typing import Any, AsyncIterable, Dict, Optional


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