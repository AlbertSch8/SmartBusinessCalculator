from dataclasses import dataclass


@dataclass
class LineItem:
    """Represents a single line item in an order."""
    name: str
    quantity: float
    unit_price: float
    vat_rate: float  # in percent, e.g. 21

    def subtotal_without_vat(self) -> float:
        """Return subtotal without VAT."""
        return self.quantity * self.unit_price

    def vat_amount(self) -> float:
        """Return VAT amount based on subtotal and VAT rate."""
        return self.subtotal_without_vat() * (self.vat_rate / 100.0)
