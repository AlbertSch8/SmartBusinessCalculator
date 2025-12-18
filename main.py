from __future__ import annotations
from typing import Dict
import threading
import queue
import tkinter as tk
from tkinter import messagebox

from src.order_manager import OrderManager
from src.models import LineItem
from src.calculation_worker import CalculationWorker
from src.json_storage import save_order_to_json, load_order_from_json
from src.logger import Logger


JSON_FILEPATH = "data/orders.json"
LOG_FILEPATH = "logs/app.log"


class BusinessCalculatorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Business Calculator (GUI)")

        # --- core objects ---
        self.logger = Logger(LOG_FILEPATH)
        self.logger.log("GUI application started")

        self.order_manager = OrderManager("Order")
        self.task_queue: "queue.Queue[str]" = queue.Queue()
        self.result_dict: Dict[str, float] = {}
        self.result_lock = threading.Lock()
        self.stop_event = threading.Event()

        self.worker = CalculationWorker(
            order_manager=self.order_manager,
            task_queue=self.task_queue,
            result_dict=self.result_dict,
            result_lock=self.result_lock,
            stop_event=self.stop_event,
            logger=self.logger,
        )
        self.worker.start()

        # --- UI variables ---
        self.order_name_var = tk.StringVar(value=self.order_manager.order_name)
        self.item_name_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.vat_var = tk.StringVar()

        self.result_var = tk.StringVar(value="Result: (no calculation yet)")

        # --- build UI ---
        self._build_ui()

        # window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        # Order name
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="Order name:").pack(side="left")
        tk.Entry(top, textvariable=self.order_name_var, width=30).pack(side="left", padx=6)
        tk.Button(top, text="Apply", command=self.apply_order_name).pack(side="left")

        # New item form
        form = tk.LabelFrame(self.root, text="Add item", padx=10, pady=10)
        form.pack(fill="x", padx=10)

        tk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.item_name_var, width=18).grid(row=0, column=1, padx=6, pady=2)

        tk.Label(form, text="Qty").grid(row=0, column=2, sticky="w")
        tk.Entry(form, textvariable=self.qty_var, width=8).grid(row=0, column=3, padx=6, pady=2)

        tk.Label(form, text="Unit price").grid(row=0, column=4, sticky="w")
        tk.Entry(form, textvariable=self.price_var, width=10).grid(row=0, column=5, padx=6, pady=2)

        tk.Label(form, text="VAT %").grid(row=0, column=6, sticky="w")
        tk.Entry(form, textvariable=self.vat_var, width=8).grid(row=0, column=7, padx=6, pady=2)

        tk.Button(form, text="Add", command=self.add_item).grid(row=0, column=8, padx=6)

        # Items list
        items_frame = tk.LabelFrame(self.root, text="Items", padx=10, pady=10)
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.items_listbox = tk.Listbox(items_frame, height=10, width=90)
        self.items_listbox.pack(fill="both", expand=True)

        # Buttons + result
        bottom = tk.Frame(self.root, padx=10, pady=10)
        bottom.pack(fill="x")

        tk.Button(bottom, text="Calculate (worker)", command=self.calculate).pack(side="left")
        tk.Button(bottom, text="Refresh items", command=self.refresh_items).pack(side="left", padx=6)
        tk.Button(bottom, text="Show result", command=self.show_result).pack(side="left", padx=6)

        tk.Button(bottom, text="Save JSON", command=self.save_json).pack(side="left", padx=18)
        tk.Button(bottom, text="Load JSON", command=self.load_json).pack(side="left", padx=6)

        tk.Label(bottom, textvariable=self.result_var).pack(side="right")

        # Initial load
        self.refresh_items()

    # --- helpers ---
    def apply_order_name(self) -> None:
        name = self.order_name_var.get().strip() or "Order"
        self.order_manager.order_name = name
        self.logger.log(f"Order name set to '{name}'")
        self.refresh_items()

    def _read_float(self, value: str) -> float:
        return float(value.strip().replace(",", "."))

    # --- actions ---
    def add_item(self) -> None:
        name = self.item_name_var.get().strip() or "Item"

        try:
            qty = self._read_float(self.qty_var.get())
            price = self._read_float(self.price_var.get())
            vat = self._read_float(self.vat_var.get())
        except ValueError:
            messagebox.showwarning("Invalid input", "Qty, price and VAT must be numbers.")
            return

        if qty < 0 or price < 0 or vat < 0:
            messagebox.showwarning("Invalid input", "Qty, price and VAT must be >= 0.")
            return

        self.apply_order_name()

        item = LineItem(name=name, quantity=qty, unit_price=price, vat_rate=vat)
        self.order_manager.add_item(item)
        self.logger.log(f"Item added: name='{name}', qty={qty}, price={price}, vat={vat}")

        # clear fields
        self.item_name_var.set("")
        self.qty_var.set("")
        self.price_var.set("")
        self.vat_var.set("")

        self.refresh_items()

    def refresh_items(self) -> None:
        self.items_listbox.delete(0, tk.END)
        items = self.order_manager.snapshot_items()

        if not items:
            self.items_listbox.insert(tk.END, "No items in the order.")
            return

        for it in items:
            self.items_listbox.insert(
                tk.END,
                f"{it.name} | qty={it.quantity} | unit={it.unit_price:.2f} | VAT={it.vat_rate:.1f}%"
            )

    def calculate(self) -> None:
        self.task_queue.put("CALCULATE")
        self.result_var.set("Result: calculating in worker thread...")
        self.logger.log("GUI: calculation task sent")

        # optional: auto-refresh result a moment later
        self.root.after(250, self.show_result)

    def show_result(self) -> None:
        with self.result_lock:
            if "subtotal" not in self.result_dict:
                self.result_var.set("Result: (no calculation yet)")
                return
            subtotal = self.result_dict["subtotal"]
            vat_total = self.result_dict["vat"]
            total = self.result_dict["total"]

        self.result_var.set(
            f"Result: Subtotal={subtotal:.2f} | VAT={vat_total:.2f} | Total={total:.2f}"
        )

    def save_json(self) -> None:
        self.apply_order_name()
        save_order_to_json(self.order_manager, JSON_FILEPATH)
        self.logger.log(f"GUI: order saved to JSON: {JSON_FILEPATH}")
        messagebox.showinfo("Saved", f"Saved to {JSON_FILEPATH}")

    def load_json(self) -> None:
        load_order_from_json(self.order_manager, JSON_FILEPATH)
        self.order_name_var.set(self.order_manager.order_name)
        self.refresh_items()
        self.show_result()
        self.logger.log(f"GUI: order loaded from JSON: {JSON_FILEPATH}")
        messagebox.showinfo("Loaded", f"Loaded from {JSON_FILEPATH}")

    def on_close(self) -> None:
        self.logger.log("GUI application closing requested")
        self.stop_event.set()
        self.task_queue.put("STOP")
        try:
            self.worker.join(timeout=1.0)
        except RuntimeError:
            pass
        self.logger.log("GUI application closed")
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    BusinessCalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
