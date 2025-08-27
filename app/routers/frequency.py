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
            SMS_Data.group_id,
            SMS_Data.ts,
            SMS_Data.text_sms,
            func.row_number().over(
                partition_by=SMS_Data.group_id,
                order_by=[SMS_Data.ts.asc(), SMS_Data.id.asc()]
            ).label("rn"),
            func.count().over(partition_by=SMS_Data.group_id).label("frequency")
        )
        .where(*filters)
        .cte("filtered_cte")
    )

    base_query = (
        select(
            filtered_cte.c.group_id,
            filtered_cte.c.frequency,
            filtered_cte.c.ts,
            filtered_cte.c.text_sms
        )
        .where(filtered_cte.c.rn == 1)
        .order_by(filtered_cte.c.ts)
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
        FrequencyResponse(
            stt=i + 1 + offset,
            group_id=r.group_id,
            text_sms=r.text_sms,
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



@router.put("/")
def feedback_base_on_frequency(
    session: Annotated[Session, Depends(get_session)],
    user_feedback: FrequencyFeedback
):
    # Bulk update
    stmt = (
        update(SMS_Data)
        .where(SMS_Data.sdt_in == user_feedback.sdt_in)
        .values(feedback=user_feedback.feedback)
    )

    result = session.exec(stmt)

    # Check the result if it is None
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Records are not found"
        )

    session.commit()

    return {
        "Message": f"Updated {result.rowcount} records",
    }
