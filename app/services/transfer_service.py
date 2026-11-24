import secrets
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.transaction import Transaction
from app.models.wallet import Wallet


MAX_BALANCE = Decimal("9999999999.99")


class IdempotencyConflict(Exception):
    """Raised when an idempotency key is reused for different details."""


def transfer_funds(
    db: Session,
    sender_user_id: int,
    receiver_wallet_id: int,
    amount: Decimal,
    idempotency_key: str,
) -> Transaction:
    """Transfer funds atomically with idempotent request handling."""

    if not amount.is_finite() or amount <= Decimal("0.00"):
        raise ValueError("Transfer amount must be greater than zero.")

    if amount.as_tuple().exponent < -2:
        raise ValueError("Transfer amount cannot exceed two decimal places.")

    idempotency_key = idempotency_key.strip()

    if not idempotency_key:
        raise ValueError("Idempotency key cannot be empty.")

    try:
        sender_wallet = db.scalar(
            select(Wallet).where(Wallet.user_id == sender_user_id)
        )

        if sender_wallet is None:
            raise ValueError("Sender wallet not found.")

        # Return the original transaction when this request was already processed.
        existing_transaction = db.scalar(
            select(Transaction).where(
                Transaction.sender_wallet_id == sender_wallet.id,
                Transaction.idempotency_key == idempotency_key,
            )
        )

        if existing_transaction is not None:
            if (
                existing_transaction.receiver_wallet_id != receiver_wallet_id
                or existing_transaction.amount != amount
            ):
                raise IdempotencyConflict(
                    "This idempotency key has already been used "
                    "with different transfer details."
                )

            return existing_transaction

        receiver_wallet = db.scalar(
            select(Wallet).where(Wallet.id == receiver_wallet_id)
        )

        if receiver_wallet is None:
            raise ValueError("Recipient wallet not found.")

        if sender_wallet.id == receiver_wallet.id:
            raise ValueError("You cannot transfer funds to your own wallet.")

        debit_result = db.execute(
            update(Wallet)
            .where(
                Wallet.id == sender_wallet.id,
                Wallet.balance >= amount,
            )
            .values(balance=Wallet.balance - amount)
            .execution_options(synchronize_session=False)
        )

        if debit_result.rowcount != 1:
            raise ValueError("Insufficient wallet balance.")

        credit_result = db.execute(
            update(Wallet)
            .where(
                Wallet.id == receiver_wallet.id,
                Wallet.balance <= MAX_BALANCE - amount,
            )
            .values(balance=Wallet.balance + amount)
            .execution_options(synchronize_session=False)
        )

        if credit_result.rowcount != 1:
            raise ValueError("Recipient wallet balance limit exceeded.")

        transaction = Transaction(
            sender_wallet_id=sender_wallet.id,
            receiver_wallet_id=receiver_wallet.id,
            amount=amount,
            transaction_type="transfer",
            status="completed",
            reference=f"TRF-{secrets.token_urlsafe(24)}",
            idempotency_key=idempotency_key,
        )

        db.add(transaction)
        db.flush()

        audit_log = AuditLog(
            actor_user_id=sender_user_id,
            action="wallet_transfer",
            resource_type="transaction",
            resource_id=str(transaction.id),
        )

        db.add(audit_log)

        db.commit()
        db.refresh(transaction)

        return transaction

    except Exception:
        db.rollback()
        raise
