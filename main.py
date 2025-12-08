from typing import Dict
import threading
import queue

from src.order_manager import OrderManager
from src.calculation_worker import CalculationWorker
from src.models import LineItem
from src.json_storage import save_order_to_json, load_order_from_json


JSON_FILEPATH = "data/orders.json"


def read_float(prompt: str) -> float:
    """Read a floating-point number from user input."""
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Invalid number, please try again.")


def print_result(result: Dict[str, float]) -> None:
    """Print the last calculation result."""
    if "subtotal" not in result:
        print("No calculation result available yet.")
        return

    print("\nLast calculation result:")
    print(f"Subtotal (without VAT): {result['subtotal']:.2f}")
    print(f"VAT total:              {result['vat']:.2f}")
    print(f"Total (with VAT):       {result['total']:.2f}\n")


def show_menu() -> None:
    """Display main menu."""
    print("============== Smart Business Calculator ==============")
    print("1) Add line item")
    print("2) List items")
    print("3) Run calculation (worker thread)")
    print("4) Show last result")
    print("5) Save order to JSON")
    print("6) Load order from JSON")
    print("0) Exit")
    print("=======================================================")


def main() -> None:
    order_name = input("Enter order name: ").strip() or "Order"
    order_manager = OrderManager(order_name)

    task_queue: "queue.Queue[str]" = queue.Queue()
    result_dict: Dict[str, float] = {}
    result_lock = threading.Lock()
    stop_event = threading.Event()

    worker = CalculationWorker(
        order_manager=order_manager,
        task_queue=task_queue,
        result_dict=result_dict,
        result_lock=result_lock,
        stop_event=stop_event,
    )
    worker.start()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Item name: ").strip() or "Item"
            quantity = read_float("Quantity: ")
            unit_price = read_float("Unit price: ")
            vat_rate = read_float("VAT rate in %: ")

            item = LineItem(
                name=name,
                quantity=quantity,
                unit_price=unit_price,
                vat_rate=vat_rate,
            )
            order_manager.add_item(item)
            print("Item added.\n")

        elif choice == "2":
            order_manager.print_items()

        elif choice == "3":
            print("Sending calculation request to worker thread...\n")
            task_queue.put("CALCULATE")

        elif choice == "4":
            with result_lock:
                print_result(result_dict)

        elif choice == "5":
            # save current order to JSON
            save_order_to_json(order_manager, JSON_FILEPATH)

        elif choice == "6":
            # load order from JSON
            load_order_from_json(order_manager, JSON_FILEPATH)

        elif choice == "0":
            print("Exiting program...")
            stop_event.set()
            task_queue.put("STOP")
            worker.join()
            break

        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
