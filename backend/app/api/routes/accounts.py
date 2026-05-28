from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.api import deps
from backend.app.schemas.account import AccountResponse
from backend.app.db.models.account import Account

router = APIRouter()

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str, 
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Returns account profile, scores, and (TODO: link transactions)
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    return account
