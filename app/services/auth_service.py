from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:
    """Register a customer and automatically create their wallet."""

    # Check whether the email is already registered.
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise ValueError("An account with this email already exists.")

    # Create the customer account.
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role="customer",
        is_active=True,
    )

    try:
        db.add(new_user)

        # Obtain the generated user ID before creating the wallet.
        db.flush()

        # Automatically create an empty wallet for the customer.
        new_wallet = Wallet(user_id=new_user.id)
        db.add(new_wallet)

        # Save both records in one database transaction.
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Account registration failed because a conflicting record exists."
        )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user using their email and password."""

    # Find the account associated with the submitted email.
    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Use the same failure response for unknown emails and
    # incorrect passwords to reduce account enumeration.
    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    # Prevent inactive accounts from authenticating.
    if not user.is_active:
        return None

    return user
