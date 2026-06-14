from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.app.api import deps
from backend.app.schemas.transaction import TransactionResponse
from backend.app.db.models.transaction import Transaction

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Returns recent transactions.
    """
    result = await db.execute(
        select(Transaction).order_by(Transaction.transaction_time.desc()).offset(skip).limit(limit)
    )
    transactions = result.scalars().all()
    return transactions
