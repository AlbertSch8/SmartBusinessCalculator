from __future__ import annotations
from typing import Dict, Optional
import threading
import queue

from .order_manager import OrderManager
from .logger import Logger


class CalculationWorker(threading.Thread):
    """
    Background worker that calculates totals for the order.

    Tasks in queue:
      - "CALCULATE" -> recompute totals
      - "STOP"      -> exit the thread loop
    """

    def __init__(
        self,
        order_manager: OrderManager,
        task_queue: "queue.Queue[str]",
        result_dict: Dict[str, float],
        result_lock: threading.Lock,
        stop_event: threading.Event,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(daemon=True)
        self.order_manager = order_manager
        self.task_queue = task_queue
        self.result_dict = result_dict
        self.result_lock = result_lock
        self.stop_event = stop_event
        self.logger = logger

    def run(self) -> None:
        if self.logger:
            self.logger.log("Worker thread started")

        while not self.stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if task == "CALCULATE":
                self._calculate()
            elif task == "STOP":
                break

        if self.logger:
            self.logger.log("Worker thread stopped")

    def _calculate(self) -> None:
        items = self.order_manager.snapshot_items()

        subtotal = sum(item.subtotal_without_vat() for item in items)
        vat_total = sum(item.vat_amount() for item in items)
        total = subtotal + vat_total

        with self.result_lock:
            self.result_dict["subtotal"] = subtotal
            self.result_dict["vat"] = vat_total
            self.result_dict["total"] = total

        # Console info stays (as you had it)
        print("\n[INFO] Calculation completed in worker thread.")
        print(f"[INFO] Subtotal (without VAT): {subtotal:.2f}")
        print(f"[INFO] VAT total:              {vat_total:.2f}")
        print(f"[INFO] Total (with VAT):       {total:.2f}\n")

        if self.logger:
            self.logger.log(
                f"Calculated totals: subtotal={subtotal:.2f}, vat={vat_total:.2f}, total={total:.2f}"
            )
