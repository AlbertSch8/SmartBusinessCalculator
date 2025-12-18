import tkinter as tk
from tkinter import messagebox

from .order_manager import OrderManager
from .json_storage import save_order_to_json, load_order_from_json
from .logger import Logger


def open_simple_gui(
    order_manager: OrderManager,
    task_queue,
    result_dict: dict,
    result_lock,
    json_filepath: str,
    logger: Logger,
) -> None:
    """
    Minimal GUI for the project.
    - Shows current items
    - Can trigger calculation (worker thread)
    - Can display last result
    - Can save/load JSON
    """

    win = tk.Tk()
    win.title("Smart Business Calculator - Simple GUI")

    # --- header ---
    header = tk.Label(win, text=f"Order: {order_manager.order_name}")
    header.pack(pady=5)

    # --- listbox with items ---
    listbox = tk.Listbox(win, width=70, height=10)
    listbox.pack(padx=10, pady=5)

    # --- result label ---
    result_var = tk.StringVar(value="No calculation result yet.")
    result_label = tk.Label(win, textvariable=result_var)
    result_label.pack(pady=5)

    def refresh_items() -> None:
        header.config(text=f"Order: {order_manager.order_name}")
        listbox.delete(0, tk.END)

        items = order_manager.snapshot_items()
        if not items:
            listbox.insert(tk.END, "No items in the order.")
            return

        for item in items:
            listbox.insert(
                tk.END,
                f"{item.name} | qty={item.quantity} | price={item.unit_price:.2f} | VAT={item.vat_rate:.1f}%"
            )

    def show_result() -> None:
        with result_lock:
            if "subtotal" not in result_dict:
                result_var.set("No calculation result yet.")
                return
            subtotal = result_dict["subtotal"]
            vat_total = result_dict["vat"]
            total = result_dict["total"]

        result_var.set(f"Subtotal: {subtotal:.2f} | VAT: {vat_total:.2f} | Total: {total:.2f}")

    def calculate_in_worker() -> None:
        task_queue.put("CALCULATE")
        result_var.set("Calculating in worker thread...")
        logger.log("GUI: calculation task sent to worker thread")

    def save_json() -> None:
        save_order_to_json(order_manager, json_filepath)
        logger.log(f"GUI: order saved to JSON: {json_filepath}")
        messagebox.showinfo("Saved", f"Order saved to {json_filepath}")

    def load_json() -> None:
        load_order_from_json(order_manager, json_filepath)
        logger.log(f"GUI: order loaded from JSON: {json_filepath}")
        refresh_items()
        show_result()

    # --- buttons ---
    btns = tk.Frame(win)
    btns.pack(pady=8)

    tk.Button(btns, text="Refresh", command=refresh_items).grid(row=0, column=0, padx=4)
    tk.Button(btns, text="Calculate", command=calculate_in_worker).grid(row=0, column=1, padx=4)
    tk.Button(btns, text="Show result", command=show_result).grid(row=0, column=2, padx=4)
    tk.Button(btns, text="Save JSON", command=save_json).grid(row=0, column=3, padx=4)
    tk.Button(btns, text="Load JSON", command=load_json).grid(row=0, column=4, padx=4)
    tk.Button(btns, text="Close", command=win.destroy).grid(row=0, column=5, padx=4)

    # initial fill
    refresh_items()
    show_result()
    logger.log("GUI opened")

    win.mainloop()
