from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, DateTime, func, Text


# ── User ─────────────────────────────────────────────────
class UserBase(SQLModel):
    """Shared fields — used for both DB and API responses."""
    email        : str  = Field(unique=True, index=True)
    username     : str  = Field(unique=True, index=True)
    is_active    : bool = Field(default=True)
    paper_balance: float = Field(default=10000.0)


class User(UserBase, table=True):
    """
    Database table.
    table=True tells SQLModel to create a real DB table.
    """
    __tablename__ = "users"

    id             : Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at     : Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationships
    searches : List["SearchHistory"] = Relationship(back_populates="user")
    watchlist: List["Watchlist"]     = Relationship(back_populates="user")
    trades   : List["PaperTrade"]    = Relationship(back_populates="user")


class UserResponse(UserBase):
    """
    API response shape — no password, adds id + created_at.
    No table=True so this is Pydantic only, not a DB table.
    """
    id        : int
    created_at: Optional[datetime]


# ── Search History ───────────────────────────────────────
class SearchHistory(SQLModel, table=True):
    __tablename__ = "search_history"

    id         : Optional[int] = Field(default=None, primary_key=True)
    user_id    : int           = Field(foreign_key="users.id")
    ticker     : str
    searched_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    user: Optional[User] = Relationship(back_populates="searches")


# ── Watchlist ────────────────────────────────────────────
class Watchlist(SQLModel, table=True):
    __tablename__ = "watchlist"

    id      : Optional[int] = Field(default=None, primary_key=True)
    user_id : int           = Field(foreign_key="users.id")
    ticker  : str
    added_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    user: Optional[User] = Relationship(back_populates="watchlist")


# ── Paper Trades ─────────────────────────────────────────
class PaperTrade(SQLModel, table=True):
    __tablename__ = "paper_trades"

    id             : Optional[int] = Field(default=None, primary_key=True)
    user_id        : int           = Field(foreign_key="users.id")
    ticker         : str
    action         : str           # 'BUY' or 'SELL'
    shares         : float
    price_at_trade : float
    total_value    : float
    traded_at      : Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    user: Optional[User] = Relationship(back_populates="trades")


# ── Model Cache ──────────────────────────────────────────
class ModelCache(SQLModel, table=True):
    """Tracks which tickers have trained models."""
    __tablename__ = "model_cache"

    id        : Optional[int] = Field(default=None, primary_key=True)
    ticker    : str           = Field(unique=True, index=True)
    trained_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    mae : Optional[float] = None
    mape: Optional[float] = None


# ── API Cache ────────────────────────────────────────────
class APICache(SQLModel, table=True):
    """Caches Alpha Vantage responses for 24 hours."""
    __tablename__ = "api_cache"

    id        : Optional[int] = Field(default=None, primary_key=True)
    ticker    : str           = Field(index=True)
    data_type : str           # 'rsi', 'macd', 'news', 'overview'
    data      : str           = Field(sa_column=Column(Text))
    fetched_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )