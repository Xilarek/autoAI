from app.models.search_request import SearchRequest
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.post("/smart")
async def smart_search(query: str, db: AsyncSession = Depends(get_db)):
    """Умный поиск по естественному запросу"""
    search_req = SearchRequest(query_text=query)
    db.add(search_req)
    await db.commit()
    return {"message": "Поиск запущен", "query": query, "search_id": search_req.id}
