from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc, column
from app.db import get_session
from app.models import Spam_Info
from datetime import datetime
from sqlalchemy import func
from app.schemas import Content_Feedback
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
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    # If datetime is not specified then use every date
    if from_datetime is None:
        from_datetime = session.exec(select(func.min(Spam_Info.ts))).one()
    if to_datetime is None:
        to_datetime = session.exec(select(func.max(Spam_Info.ts))).one()

    filters = [
        Spam_Info.ts >= from_datetime,
        Spam_Info.ts <= to_datetime
    ]
    if phone_num:
        filters.append(Spam_Info.sdt_in.ilike(f"%{phone_num}%"))


    # Get the amount of message of a phone number in a period of time
    cte1 = (
        select(
            Spam_Info.sdt_in,
            func.count().label("frequency")
        )
        .where(*filters)
        .group_by(Spam_Info.sdt_in)
        .cte("cte1")
    )

    cte2 = (
        select(
            Spam_Info.sdt_in,
            Spam_Info.ts,
            func.row_number().over(
                partition_by=Spam_Info.sdt_in,
                order_by=Spam_Info.ts
            ).label("row_num")
        )
        .where(*filters)
        .cte("cte2")
    )

    base_query = (
        select(
            cte2.c.sdt_in,
            cte1.c.frequency,
            cte2.c.ts
        )
        .join(cte1, cte1.c.sdt_in == cte2.c.sdt_in)
        .where(cte2.c.row_num == 1)
        .order_by(cte2.c.ts)
    )


    sub = base_query.subquery()
    total_rows = session.exec(select(func.count()).select_from(sub)).one()
    total_pages = ceil(total_rows/page_size)

    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )

    
    # Calculate the offset and query with the offset 
    offset = (page - 1) * page_size
    paginated_query = base_query.offset(offset).limit(page_size).order_by(cte2.c.ts, cte1.c.frequency.desc())
    records = session.exec(paginated_query).all()

    return [
        {"stt": i + 1 + offset, **dict(r._mapping)}
        for i, r in enumerate(records)
    ]

    
    


