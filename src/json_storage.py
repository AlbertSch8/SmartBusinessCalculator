"""
json_storage.py
--------------
Module responsible for saving and loading order data to/from JSON files.

This is only a skeleton for now. The actual implementation will come
in later commits.
"""

import json
from typing import Any
from .order_manager import OrderManager


def save_order_to_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Save the current order to a JSON file.

    Implementation will be added in a later commit.
    """
    pass


def load_order_from_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Load order data from a JSON file and populate the OrderManager.

    Implementation will be added in a later commit.
    """
    pass