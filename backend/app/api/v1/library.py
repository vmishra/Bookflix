"""Library management endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services import library_service
from app.schemas.processing import ScanRequest, ScanResponse, LibraryStatsOut
from app.config import settings

router = APIRouter()


@router.post("/scan", response_model=ScanResponse)
async def scan_library(request: ScanRequest):
    from celery_app.tasks.book_tasks import scan_library as scan_task
    task = scan_task.delay(request.directory)
    return ScanResponse(
        task_id=task.id,
        directory=request.directory,
        message="Scan started",
    )


@router.get("/scan/{task_id}")
async def get_scan_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@router.post("/import")
async def import_books(
    directory: str | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    dir_path = directory or settings.books_path
    files = await library_service.scan_books_directory(dir_path)
    result = await library_service.import_books(db, files)
    return result


@router.get("/stats", response_model=LibraryStatsOut)
async def library_stats(db: AsyncSession = Depends(get_async_session)):
    stats = await library_service.get_library_stats(db)
    return LibraryStatsOut(**stats)


@router.get("/processing")
async def get_processing_status(db: AsyncSession = Depends(get_async_session)):
    from sqlalchemy import select, func
    from app.models.processing import ProcessingJob

    result = await db.execute(
        select(
            ProcessingJob.status,
            func.count(ProcessingJob.id),
        ).group_by(ProcessingJob.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}

    # Get recent failures
    result = await db.execute(
        select(ProcessingJob)
        .where(ProcessingJob.status == "failed")
        .order_by(ProcessingJob.updated_at.desc())
        .limit(10)
    )
    failures = result.scalars().all()

    return {
        "status_counts": status_counts,
        "recent_failures": [
            {
                "id": j.id,
                "book_id": j.book_id,
                "stage": j.stage,
                "error": j.error_message,
            }
            for j in failures
        ],
    }
