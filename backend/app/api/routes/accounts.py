from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.api import deps
from backend.app.schemas.account import AccountResponse
from backend.app.db.models.account import Account

router = APIRouter()

@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db)
):
    """Returns a paginated list of all accounts."""
    result = await db.execute(select(Account).offset(skip).limit(limit))
    return result.scalars().all()

from sqlalchemy import or_
from backend.app.db.models.transaction import Transaction

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str, 
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Returns account profile, scores, and linked transactions
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Fetch linked transactions
    tx_result = await db.execute(
        select(Transaction).where(
            or_(
                Transaction.sender_account_id == account_id,
                Transaction.receiver_account_id == account_id
            )
        )
    )
    transactions = tx_result.scalars().all()
    account.transactions = list(transactions)
        
    return account
