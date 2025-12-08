"""
json_storage.py
--------------
Module responsible for saving and loading order data to/from JSON files.

Commit 2: Skeleton
Commit 3: JSON save implementation
Commit 4: JSON load implementation
"""

import json
from .order_manager import OrderManager
from .models import LineItem


def save_order_to_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Save the current order to a JSON file.
    Converts all line items into a serializable dict structure.
    """

    data = {
        "order_name": order_manager.order_name,
        "items": []
    }

    # Convert items to dicts for JSON
    for item in order_manager.snapshot_items():
        data["items"].append({
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "vat_rate": item.vat_rate
        })

    # Save JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Order saved to JSON: {filepath}")


def load_order_from_json(order_manager: OrderManager, filepath: str) -> None:
    """
    Load order data from a JSON file and populate the OrderManager.
    Existing items will be replaced.
    """

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[WARN] JSON file not found: {filepath}")
        return
    except json.JSONDecodeError:
        print(f"[WARN] Failed to parse JSON file: {filepath}")
        return

    # Validate data
    if not isinstance(data, dict):
        print("[WARN] JSON has unexpected format (root is not an object).")
        return

    # Load order name
    name = data.get("order_name")
    if isinstance(name, str) and name.strip():
        order_manager.order_name = name.strip()

    # Load items list
    items_data = data.get("items", [])
    if not isinstance(items_data, list):
        print("[WARN] JSON has unexpected format (items is not a list).")
        return

    loaded_items: list[LineItem] = []

    for item_dict in items_data:
        if not isinstance(item_dict, dict):
            continue

        try:
            loaded_items.append(
                LineItem(
                    name=str(item_dict.get("name", "Item")),
                    quantity=float(item_dict.get("quantity", 0)),
                    unit_price=float(item_dict.get("unit_price", 0)),
                    vat_rate=float(item_dict.get("vat_rate", 0)),
                )
            )
        except (TypeError, ValueError):
            # Skip badly formatted item
            continue

    if not loaded_items:
        print("[WARN] No valid items found in JSON.")
        return

    # Replace items inside order manager
    order_manager.replace_items(loaded_items)
    print(f"[INFO] Order loaded from JSON: {filepath}")