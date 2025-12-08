"""
json_storage.py
--------------
Module responsible for saving and loading order data to/from JSON files.

Commit 2: Skeleton
Commit 3: Added save_order_to_json implementation
"""

import json
from typing import Any
from .order_manager import OrderManager


def save_order_to_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Save the current order to a JSON file.
    Converts all line items into a serializable dict structure.
    """

    data = {
        "order_name": order_manager.order_name,
        "items": []
    }

    # převést položky na slovníky
    for item in order_manager.snapshot_items():
        data["items"].append({
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "vat_rate": item.vat_rate
        })

    # uložit do JSON souboru
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Order saved to JSON: {filepath}")


def load_order_from_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Load order data from a JSON file and populate the OrderManager.

    (Implementation will be added in Commit 4)
    """
    pass
