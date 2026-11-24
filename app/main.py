from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.wallets import router as wallets_router
from app.api.transactions import router as transactions_router
from app.core.limiter import limiter


app = FastAPI(
    title="SecureWallet API",
    description="A security-focused simulated digital wallet API.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(auth_router)
app.include_router(wallets_router)
app.include_router(transactions_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "application": "SecureWallet API",
        "version": "1.0.0",
    }
