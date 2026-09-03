from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class CustomerEntity:
    id: UUID | None
    full_name: str
    phone: str
    email: str
    is_active: bool = True
    deleted_at: datetime | None = None
