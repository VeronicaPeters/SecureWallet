from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.wallet import WalletFunding, WalletResponse

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return wallet


@router.post("/fund", response_model=WalletResponse)
def fund_my_wallet(
    funding: WalletFunding,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services.wallet_service import fund_wallet

    try:
        return fund_wallet(
            db=db,
            user_id=current_user.id,
            amount=funding.amount,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
