from typing import List
import threading
from .models import LineItem


class OrderManager:
    """Manages a single order and its line items in a thread-safe way."""

    def __init__(self, order_name: str) -> None:
        self.order_name = order_name
        self._items: List[LineItem] = []
        self._lock = threading.Lock()

    def add_item(self, item: LineItem) -> None:
        """Add a new item to the order in a thread-safe way."""
        with self._lock:
            self._items.append(item)

    def snapshot_items(self) -> List[LineItem]:
        """
        Return a copy of the current items.
        Used by the worker thread to safely iterate over items.
        """
        with self._lock:
            return list(self._items)

    def replace_items(self, items: List[LineItem]) -> None:
        """
        Replace current items with a new list.
        Used when loading data from a JSON file.
        """
        with self._lock:
            self._items = list(items)

    def print_items(self) -> None:
        """Print all items in the order."""
        items = self.snapshot_items()
        if not items:
            print("The order has no items yet.")
            return

        print(f"\nItems in order '{self.order_name}':")
        print("-" * 60)
        for i, item in enumerate(items, start=1):
            print(
                f"{i}. {item.name} | quantity: {item.quantity} | "
                f"unit price: {item.unit_price:.2f} | VAT: {item.vat_rate:.1f}%"
            )
        print("-" * 60)
