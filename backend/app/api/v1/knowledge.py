"""Knowledge/second brain endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import knowledge_service
from app.schemas.book import BookOut

router = APIRouter()


@router.get("/connections")
async def get_connections(limit: int = 50, db: AsyncSession = Depends(get_async_session)):
    connections = await knowledge_service.get_knowledge_connections(db, limit=limit)
    results = []
    for conn in connections:
        results.append({
            "connection_type": conn["connection"].connection_type,
            "strength": conn["connection"].strength,
            "insight_a": {
                "title": conn["insight_a"]["insight"].title,
                "book_title": conn["insight_a"]["book"].title if conn["insight_a"]["book"] else None,
            },
            "insight_b": {
                "title": conn["insight_b"]["insight"].title,
                "book_title": conn["insight_b"]["book"].title if conn["insight_b"]["book"] else None,
            },
        })
    return results


@router.get("/learning-paths")
async def list_learning_paths(db: AsyncSession = Depends(get_async_session)):
    paths = await knowledge_service.get_learning_paths(db)
    return [{"id": p.id, "title": p.title, "description": p.description} for p in paths]


@router.get("/learning-paths/{path_id}")
async def get_learning_path(path_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await knowledge_service.get_learning_path(db, path_id)
    if not result:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return {
        "path": {"id": result["path"].id, "title": result["path"].title, "description": result["path"].description},
        "books": [
            {"book": BookOut.model_validate(b["book"]), "position": b["position"], "rationale": b["rationale"]}
            for b in result["books"]
        ],
    }


@router.get("/map")
async def knowledge_map(db: AsyncSession = Depends(get_async_session)):
    return await knowledge_service.get_knowledge_map(db)
