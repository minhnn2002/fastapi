from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, update
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from datetime import datetime
from sqlalchemy import func
from math import ceil

router = APIRouter(
    prefix="/frequency",
    tags=['Frequency']
)


@router.get("/")
def get_spam_base_on_frequency(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    # If datetime is not specified then use every date
    if from_datetime is None:
        from_datetime = session.exec(select(func.min(SMS_Data.ts))).one()
    if to_datetime is None:
        to_datetime = session.exec(select(func.max(SMS_Data.ts))).one()

    filters = [
        SMS_Data.ts >= from_datetime,
        SMS_Data.ts <= to_datetime
    ]
    if phone_num:
        filters.append(SMS_Data.sdt_in.ilike(f"%{phone_num}%"))
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))

    # CTE used for filter data 
    filtered_cte = (
        select(
            SMS_Data.sdt_in,
            SMS_Data.ts
        )
        .where(*filters)
        .cte("filtered_cte")
    )

    # The query to get the frequency and the earliest timestamp of each phone number
    base_query = (
        select(
            filtered_cte.c.sdt_in,
            func.count().label("frequency"),
            func.min(filtered_cte.c.ts).label("ts")
        )
        .group_by(filtered_cte.c.sdt_in)
        .order_by(func.min(filtered_cte.c.ts))
    )

    # A validation for total pages
    sub = base_query.subquery()
    total_rows = session.exec(select(func.count()).select_from(sub)).one()
    total_pages = ceil(total_rows/page_size)

    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )
    
    # Calculate the offset and query with the offset 
    offset = page * page_size
    paginated_query = base_query.offset(offset).limit(page_size)
    records = session.exec(paginated_query).all()

    result = [
        BaseData(
            stt=i + 1 + offset,
            sdt_in=r.sdt_in,
            frequency=r.frequency,
            ts=r.ts
        )
        for i, r in enumerate(records)
    ]

    return BasePaginatedResponseFrequency(
        status_code=200,
        message="Success",
        data=result,
        error=False,
        error_message="",
        page=page,
        limit=page_size,
        total=total_rows
    )



@router.post("/")
def feedback_base_on_frequency(
    session: Annotated[Session, Depends(get_session)],
    user_feedback: FrequencyFeedback
):
    # bulk update
    stmt = (
        update(SMS_Data)
        .where(SMS_Data.sdt_in == user_feedback.sdt_in)
        .values(feedback=user_feedback.feedback)
    )

    result = session.exec(stmt)

    # check the result if it is None
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Records are not found"
        )

    session.commit()

    return {
        "Message": f"Updated {result.rowcount} records",
    }
