from typing import Annotated, Literal
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlmodel import Session, select
from app.db import get_session
from app.models import Spam_Info
from datetime import datetime
from sqlalchemy import func
from app.schemas import Out

router = APIRouter(
    prefix="/content",
    tags=['Content']
)


@router.get("/")
def get_spam_base_on_content(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10
):
# If datetime is not specified then use every date
    if from_datetime is None:
        from_datetime = session.exec(select(func.min(Spam_Info.ts))).one()
    if to_datetime is None:
        to_datetime = session.exec(select(func.max(Spam_Info.ts))).one()

# SQL query to calculate total rows
    base_query = (
        select(
            Spam_Info.sdt_in,
            Spam_Info.text_sms,
            func.count().label("frequency"),
            Spam_Info.ts
        )
        .where(Spam_Info.ts >= from_datetime)
        .where(Spam_Info.ts <= to_datetime)
        .group_by(Spam_Info.sdt_in, Spam_Info.text_sms, Spam_Info.ts)
    )

    sub = base_query.subquery()
    total_rows = session.exec(select(func.count()).select_from(sub)).one()
    total_pages = (total_rows + page_size - 1) // page_size

    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )

    
# Calculate the offset and query with the offset 
    offset = (page - 1) * page_size
    paginated_query = base_query.offset(offset).limit(page_size).order_by(Spam_Info.ts)
    records = session.exec(paginated_query).all()

    return [
        {"stt": i + 1 + offset, **dict(r._mapping)}
        for i, r in enumerate(records)
    ]

# @router.post("/")
# def feedback_spam_base_on_content():
    


