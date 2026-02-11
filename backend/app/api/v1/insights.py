"""Insight endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import insight_service
from app.schemas.insight import InsightOut, InsightConnectionOut, BookInsightsResponse

router = APIRouter()


@router.get("/book/{book_id}", response_model=BookInsightsResponse)
async def get_book_insights(book_id: int, db: AsyncSession = Depends(get_async_session)):
    all_insights = await insight_service.get_book_insights(db, book_id)

    concepts = [InsightOut.model_validate(i) for i in all_insights if i.insight_type == "key_concept"]
    frameworks = [InsightOut.model_validate(i) for i in all_insights if i.insight_type == "framework"]
    takeaways = [InsightOut.model_validate(i) for i in all_insights if i.insight_type == "takeaway"]

    return BookInsightsResponse(
        book_id=book_id,
        concepts=concepts,
        frameworks=frameworks,
        takeaways=takeaways,
    )


@router.get("/{insight_id}", response_model=InsightOut)
async def get_insight(insight_id: int, db: AsyncSession = Depends(get_async_session)):
    from app.models.insight import BookInsight
    insight = await db.get(BookInsight, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return InsightOut.model_validate(insight)


@router.get("/{insight_id}/connections", response_model=list[InsightConnectionOut])
async def get_insight_connections(
    insight_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_session),
):
    connections = await insight_service.find_insight_connections(db, insight_id, limit=limit)
    return [InsightConnectionOut(**c) for c in connections]


@router.get("/concepts", response_model=list[InsightOut])
async def get_all_concepts(
    limit: int = 50,
    db: AsyncSession = Depends(get_async_session),
):
    from sqlalchemy import select, desc
    from app.models.insight import BookInsight
    result = await db.execute(
        select(BookInsight)
        .where(BookInsight.insight_type == "key_concept")
        .order_by(desc(BookInsight.importance))
        .limit(limit)
    )
    return [InsightOut.model_validate(i) for i in result.scalars().all()]


@router.get("/frameworks", response_model=list[InsightOut])
async def get_all_frameworks(
    limit: int = 50,
    db: AsyncSession = Depends(get_async_session),
):
    from sqlalchemy import select, desc
    from app.models.insight import BookInsight
    result = await db.execute(
        select(BookInsight)
        .where(BookInsight.insight_type == "framework")
        .order_by(desc(BookInsight.importance))
        .limit(limit)
    )
    return [InsightOut.model_validate(i) for i in result.scalars().all()]


@router.post("/book/{book_id}/regenerate")
async def regenerate_insights(book_id: int):
    from celery_app.tasks.insight_tasks import generate_book_insights
    task = generate_book_insights.delay(book_id, pass_level=1)
    return {"task_id": task.id, "message": "Insight regeneration started"}
