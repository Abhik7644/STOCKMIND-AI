from sqlmodel import Session, select
from src.auth.models import (User, SearchHistory,
                              Watchlist, PaperTrade)
from src.auth.security import hash_password, verify_password


# ── Users ─────────────────────────────────────────────────
def create_user(db: Session, email: str,
                username: str, password: str) -> User:
    user = User(
        email          = email,
        username       = username,
        hashed_password= hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def authenticate_user(db: Session, email: str,
                      password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ── Search History ────────────────────────────────────────
def add_search(db: Session, user_id: int, ticker: str):
    search = SearchHistory(user_id=user_id, ticker=ticker)
    db.add(search)
    db.commit()


def get_search_history(db: Session,
                       user_id: int, limit: int = 10):
    return db.exec(
        select(SearchHistory)
        .where(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.searched_at.desc())
        .limit(limit)
    ).all()


# ── Watchlist ─────────────────────────────────────────────
def add_to_watchlist(db: Session,
                     user_id: int, ticker: str) -> Watchlist:
    existing = db.exec(
        select(Watchlist)
        .where(Watchlist.user_id == user_id,
               Watchlist.ticker  == ticker)
    ).first()
    if existing:
        return existing

    item = Watchlist(user_id=user_id, ticker=ticker)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_watchlist(db: Session, user_id: int):
    return db.exec(
        select(Watchlist)
        .where(Watchlist.user_id == user_id)
        .order_by(Watchlist.added_at.desc())
    ).all()


def remove_from_watchlist(db: Session,
                          user_id: int, ticker: str):
    item = db.exec(
        select(Watchlist)
        .where(Watchlist.user_id == user_id,
               Watchlist.ticker  == ticker)
    ).first()
    if item:
        db.delete(item)
        db.commit()


# ── Paper Trading ─────────────────────────────────────────
def execute_trade(db: Session, user_id: int, ticker: str,
                  action: str, shares: float,
                  current_price: float) -> PaperTrade:

    user        = get_user_by_id(db, user_id)
    total_value = shares * current_price

    if action == 'BUY':
        if user.paper_balance < total_value:
            raise ValueError("Insufficient paper balance")
        user.paper_balance -= total_value
    elif action == 'SELL':
        user.paper_balance += total_value

    trade = PaperTrade(
        user_id       = user_id,
        ticker        = ticker,
        action        = action,
        shares        = shares,
        price_at_trade= current_price,
        total_value   = total_value
    )
    db.add(user)
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def get_trades(db: Session, user_id: int):
    return db.exec(
        select(PaperTrade)
        .where(PaperTrade.user_id == user_id)
        .order_by(PaperTrade.traded_at.desc())
    ).all()