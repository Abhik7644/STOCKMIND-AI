from sqlmodel import SQLModel


# ── Auth ─────────────────────────────────────────────────
class RegisterRequest(SQLModel):
    email   : str
    username: str
    password: str

class LoginRequest(SQLModel):
    email   : str
    password: str

class TokenResponse(SQLModel):
    access_token: str
    token_type  : str = "bearer"


# ── Watchlist ────────────────────────────────────────────
class WatchlistAdd(SQLModel):
    ticker: str


# ── Paper Trading ────────────────────────────────────────
class TradeRequest(SQLModel):
    ticker: str
    action: str    # 'BUY' or 'SELL'
    shares: float