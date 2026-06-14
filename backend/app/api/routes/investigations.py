from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from backend.app.api import deps
from backend.app.schemas.investigation import InvestigationResponse, InvestigationCreate
from backend.app.db.models.investigation import Investigation

router = APIRouter()

@router.get("/", response_model=List[InvestigationResponse])
async def get_investigations(
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(deps.get_db)
):
    result = await db.execute(
        select(Investigation).order_by(Investigation.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=InvestigationResponse)
async def create_investigation(
    inv: InvestigationCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    db_inv = Investigation(**inv.model_dump())
    db.add(db_inv)
    await db.commit()
    await db.refresh(db_inv)
    return db_inv
