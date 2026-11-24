from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.transaction import TransferCreate, TransactionResponse
from app.services.transfer_service import (
    IdempotencyConflict,
    transfer_funds,
)
from app.services.transaction_service import get_user_transactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transfer(
    transfer: TransferCreate,
    idempotency_key: str = Header(
        alias="Idempotency-Key",
        min_length=8,
        max_length=128,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return transfer_funds(
            db=db,
            sender_user_id=current_user.id,
            receiver_wallet_id=transfer.receiver_wallet_id,
            amount=transfer.amount,
            idempotency_key=idempotency_key,
        )
    except IdempotencyConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/me",
    response_model=list[TransactionResponse],
)
def get_my_transactions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
