from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

@dataclass
class ProductEntity:
    id: UUID | None
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    is_available: bool = True
    is_active: bool = True
