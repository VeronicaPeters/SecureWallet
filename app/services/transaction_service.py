from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.wallet import Wallet


def get_user_transactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> list[Transaction]:
    """Return only transactions involving the authenticated user's wallet."""

    user_wallet_ids = select(Wallet.id).where(
        Wallet.user_id == user_id
    )

    statement = (
        select(Transaction)
        .where(
            or_(
                Transaction.sender_wallet_id.in_(user_wallet_ids),
                Transaction.receiver_wallet_id.in_(user_wallet_ids),
            )
        )
        .order_by(
            Transaction.created_at.desc(),
            Transaction.id.desc(),
        )
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())
