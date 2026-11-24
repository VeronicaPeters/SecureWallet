from app.core.database import Base, engine

# Import all models so SQLAlchemy registers their tables.
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.audit_log import AuditLog


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
