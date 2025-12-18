from typing import Dict
import threading
import queue

from src.order_manager import OrderManager
from src.calculation_worker import CalculationWorker
from src.models import LineItem
from src.json_storage import save_order_to_json, load_order_from_json
from src.logger import Logger
from src.simple_gui import open_simple_gui


JSON_FILEPATH = "data/orders.json"
LOG_FILEPATH = "logs/app.log"


def read_float(prompt: str) -> float:
    """Read a floating-point number from user input."""
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("[WARN] Invalid number, please try again.")


def print_result(result: Dict[str, float]) -> None:
    """Print the last calculation result."""
    if "subtotal" not in result:
        print("[WARN] No calculation result available yet.")
        return

    print("\n[INFO] Last calculation result:")
    print(f"Subtotal (without VAT): {result['subtotal']:.2f}")
    print(f"VAT total:              {result['vat']:.2f}")
    print(f"Total (with VAT):       {result['total']:.2f}\n")


def show_menu() -> None:
    """Display main menu."""
    print("\n============== Smart Business Calculator ==============")
    print("1) Add line item")
    print("2) List items")
    print("3) Run calculation (worker thread)")
    print("4) Show last calculation result")
    print("5) Save order to JSON")
    print("6) Load order from JSON")
    print("7) Open simple GUI")
    print("0) Exit")
    print("=======================================================\n")


def main() -> None:
    logger = Logger(LOG_FILEPATH)
    logger.log("Application started")

    order_name = input("Enter order name: ").strip() or "Order"
    order_manager = OrderManager(order_name)
    logger.log(f"Order created: name='{order_manager.order_name}'")

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
        logger=logger,
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

            item = LineItem(name=name, quantity=quantity, unit_price=unit_price, vat_rate=vat_rate)
            order_manager.add_item(item)
            print("[INFO] Item added.\n")
            logger.log(
                f"Item added: name='{item.name}', qty={item.quantity}, price={item.unit_price}, vat={item.vat_rate}"
            )

        elif choice == "2":
            order_manager.print_items()
            logger.log("Items listed")

        elif choice == "3":
            print("[INFO] Sending calculation task to worker thread...\n")
            task_queue.put("CALCULATE")
            logger.log("Calculation task sent to worker thread")

        elif choice == "4":
            with result_lock:
                print_result(result_dict)
            logger.log("Result displayed")

        elif choice == "5":
            save_order_to_json(order_manager, JSON_FILEPATH)
            logger.log(f"Order saved to JSON: {JSON_FILEPATH}")

        elif choice == "6":
            load_order_from_json(order_manager, JSON_FILEPATH)
            logger.log(f"Order loaded from JSON: {JSON_FILEPATH}")

        elif choice == "7":
            open_simple_gui(
                order_manager=order_manager,
                task_queue=task_queue,
                result_dict=result_dict,
                result_lock=result_lock,
                json_filepath=JSON_FILEPATH,
                logger=logger,
            )

        elif choice == "0":
            print("[INFO] Exiting program...")
            logger.log("Application exiting requested")
            stop_event.set()
            task_queue.put("STOP")
            worker.join()
            logger.log("Application terminated")
            break

        else:
            print("[WARN] Invalid choice.\n")
            logger.log(f"Invalid menu choice: '{choice}'")


if __name__ == "__main__":
    main()
