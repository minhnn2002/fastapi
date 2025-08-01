from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlmodel import Session, select, desc, text, column
from app.db import get_session
from app.models import Spam_Info
from datetime import datetime
from sqlalchemy import func
from app.schemas import Content_Feedback
from math import ceil

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
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    # If datetime is not specified then use every date
    if from_datetime is None:
        from_datetime = session.exec(select(func.min(Spam_Info.ts))).one()
    if to_datetime is None:
        to_datetime = session.exec(select(func.max(Spam_Info.ts))).one()

    if to_datetime < from_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time range: 'to_datetime' is earlier than 'from_datetime'."
        )

    # Create all the filter needed
    filters = [
        Spam_Info.ts >= from_datetime,
        Spam_Info.ts <= to_datetime
    ]
    if text_keyword:
        filters.append(Spam_Info.text_sms.ilike(f"%{text_keyword}%"))
    if phone_num:
        filters.append(Spam_Info.sdt_in.ilike(f"%{phone_num}%"))

    # Count the frequency of message 
    cte1 = (
        select(
            Spam_Info.sdt_in,
            func.count().label("frequency")
        )
        .where(*filters)
        .group_by(Spam_Info.sdt_in)
        .cte("cte1")
    )
    
    # Get the messages 
    cte2 = (
        select(
            Spam_Info.sdt_in,
            Spam_Info.text_sms,
            Spam_Info.ts
        )
        .where(*filters)
        .cte("cte2")
    )

    # Do the query
    query = (
        select(
            cte1.c.sdt_in,
            cte1.c.frequency,
            cte2.c.text_sms,
            cte2.c.ts
        )
        .join(cte2, cte1.c.sdt_in == cte2.c.sdt_in)
        .order_by(cte2.c.ts)
    ) 
    records = session.exec(query).all()

    # Format the result
    result = {}
    stt = 0
    for record in records:
        sdt = record.sdt_in
        if sdt not in result:
            result[sdt] = {
                "stt": stt + 1,
                "sdt_in": sdt,
                "frequency": record.frequency,
                "message": [],
                "ts": record.ts
            }
            result[sdt]["message"].append({
                "content": record.text_sms,
                "count": 1
            })
            stt += 1
        else:
            found = False
            for msg in result[sdt]["message"]:
                if msg["content"] == record.text_sms:
                    msg["count"] += 1
                    found = True
                    break
            if not found:
                result[sdt]["message"].append({
                    "content": record.text_sms,
                    "count": 1
                })

    final =  list(result.values())

    total_pages = ceil(len(final)/page_size)
    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )

    return final[(page-1)*page_size:page*page_size]


