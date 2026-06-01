from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from src.database import get_db
from src.auth import crud
from src.auth.schemas import (
    RegisterRequest, LoginRequest,
    TokenResponse, WatchlistAdd, TradeRequest
)
from src.auth.models import User, UserResponse
from src.auth.security import create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Get current logged in user ────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db   : Session = Depends(get_db)
) -> User:
    """Extract and verify user from JWT token."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=404,
            detail="Invalid token"
        )
    user = crud.get_user_by_id(db, user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Register ──────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse)
def register(
    request: RegisterRequest,
    db     : Session = Depends(get_db)
):
    """Create new account, return JWT token."""
    if crud.get_user_by_email(db, request.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    user  = crud.create_user(
        db, request.email,
        request.username,
        request.password
    )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ── Login ─────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db     : Session = Depends(get_db)
):
    """Login, return JWT token."""
    user = crud.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ── Profile ───────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user


# ── Search History ────────────────────────────────────────
@router.get("/history")
def search_history(
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Get last 10 searches."""
    history = crud.get_search_history(db, current_user.id)
    return {
        "history": [
            {
                "ticker"     : h.ticker,
                "searched_at": h.searched_at
            }
            for h in history
        ]
    }


# ── Watchlist ─────────────────────────────────────────────
@router.post("/watchlist")
def add_watchlist(
    item        : WatchlistAdd,
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Add stock to watchlist."""
    crud.add_to_watchlist(db, current_user.id, item.ticker.upper())
    return {"message": f"{item.ticker.upper()} added to watchlist ✅"}


@router.get("/watchlist")
def get_watchlist(
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Get user watchlist."""
    items = crud.get_watchlist(db, current_user.id)
    return {
        "watchlist": [
            {
                "ticker"  : i.ticker,
                "added_at": i.added_at
            }
            for i in items
        ]
    }


@router.delete("/watchlist/{ticker}")
def remove_watchlist(
    ticker      : str,
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Remove stock from watchlist."""
    crud.remove_from_watchlist(db, current_user.id, ticker.upper())
    return {"message": f"{ticker.upper()} removed from watchlist"}


# ── Paper Trading ─────────────────────────────────────────
@router.post("/trade")
def execute_trade(
    request     : TradeRequest,
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Execute a paper trade with virtual money."""
    import yfinance as yf
    import pandas as pd

    # Get current real price
    df = yf.download(
        request.ticker,
        period="2d",
        progress=False
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail=f"Could not fetch price for {request.ticker}"
        )

    current_price = float(df['Close'].iloc[-1])

    try:
        trade = crud.execute_trade(
            db,
            current_user.id,
            request.ticker.upper(),
            request.action.upper(),
            request.shares,
            current_price
        )
        return {
            "message"      : f"{request.action.upper()} order executed ✅",
            "ticker"       : trade.ticker,
            "shares"       : trade.shares,
            "price"        : trade.price_at_trade,
            "total_value"  : trade.total_value,
            "new_balance"  : current_user.paper_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trades")
def get_trades(
    current_user: User    = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    """Get all paper trades + current balance."""
    trades = crud.get_trades(db, current_user.id)
    return {
        "balance": current_user.paper_balance,
        "trades" : [
            {
                "ticker"        : t.ticker,
                "action"        : t.action,
                "shares"        : t.shares,
                "price_at_trade": t.price_at_trade,
                "total_value"   : t.total_value,
                "traded_at"     : t.traded_at
            }
            for t in trades
        ]
    }