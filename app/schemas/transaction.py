from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransferCreate(BaseModel):
    receiver_wallet_id: int = Field(gt=0)
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    model_config = ConfigDict(extra="forbid")


class TransactionResponse(BaseModel):
    id: int
    sender_wallet_id: int | None
    receiver_wallet_id: int
    amount: Decimal
    transaction_type: str
    status: str
    reference: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
