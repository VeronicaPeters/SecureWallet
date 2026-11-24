import secrets
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.transaction import Transaction
from app.models.wallet import Wallet


MAX_BALANCE = Decimal("9999999999.99")


def fund_wallet(
    db: Session,
    user_id: int,
    amount: Decimal,
) -> Wallet:
    """Simulate wallet funding and record the financial activity."""

    if not amount.is_finite() or amount <= Decimal("0.00"):
        raise ValueError("Funding amount must be greater than zero.")

    if amount.as_tuple().exponent < -2:
        raise ValueError("Funding amount cannot exceed two decimal places.")

    try:
        # Atomically update only the authenticated user's wallet.
        result = db.execute(
            update(Wallet)
            .where(
                Wallet.user_id == user_id,
                Wallet.balance <= MAX_BALANCE - amount,
            )
            .values(balance=Wallet.balance + amount)
        )

        if result.rowcount != 1:
            raise ValueError(
                "Wallet not found or funding would exceed the balance limit."
            )

        wallet = db.scalar(
            select(Wallet).where(Wallet.user_id == user_id)
        )

        # Record the completed funding transaction.
        transaction = Transaction(
            sender_wallet_id=None,
            receiver_wallet_id=wallet.id,
            amount=amount,
            transaction_type="funding",
            status="completed",
            reference=f"FUND-{secrets.token_urlsafe(24)}",
        )

        db.add(transaction)

        # Record the security audit event.
        audit_log = AuditLog(
            actor_user_id=user_id,
            action="wallet_funded",
            resource_type="wallet",
            resource_id=wallet.id,
        )

        db.add(audit_log)

        # Commit balance, transaction, and audit record together.
        db.commit()
        db.refresh(wallet)

        return wallet

    except Exception:
        db.rollback()
        raise
