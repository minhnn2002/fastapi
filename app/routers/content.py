from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlmodel import Session, select, func
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from datetime import datetime
from math import ceil
from collections import defaultdict

router = APIRouter(
    prefix="/content",
    tags=['Content']
)


@router.get("/")
def get_spam_base_on_content(
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

    if to_datetime < from_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time range: 'to_datetime' is earlier than 'from_datetime'."
        )

    # Create all the filter needed
    filters = [
        SMS_Data.ts >= from_datetime,
        SMS_Data.ts <= to_datetime
    ]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))
    if phone_num:
        filters.append(SMS_Data.sdt_in.ilike(f"%{phone_num}%"))

    # CTE used for filter data 
    filtered_cte = (
        select(
            SMS_Data.sdt_in,
            SMS_Data.group_id,
            SMS_Data.text_sms,
            SMS_Data.ts
        )
        .where(*filters)
        .cte("filtered_cte")  
    )

    # CTE for counting the frequency of each sdt_in
    frequency_cte = (
        select(
            filtered_cte.c.sdt_in,
            func.count().label("frequency")
        )
        .group_by(filtered_cte.c.sdt_in)
        .cte("frequency_cte")
    )

    # Do the query
    query = (
        select(
            frequency_cte.c.sdt_in,
            frequency_cte.c.frequency,
            filtered_cte.c.group_id,
            filtered_cte.c.text_sms,
            filtered_cte.c.ts
        )
        .join(
            filtered_cte,
            frequency_cte.c.sdt_in == filtered_cte.c.sdt_in
        )
        .order_by(filtered_cte.c.ts)
    ) 
    records = session.exec(query).all()

    grouped_data = defaultdict(lambda: {
        "frequency": 0,
        "ts": None,
        "message_groups": defaultdict(lambda: defaultdict(int))
    })

    for record in records:
        key = record.sdt_in
        grouped = grouped_data[key]
        grouped["frequency"] += 1

        # Get the earliest timestamp
        if grouped["ts"] is None or record.ts < grouped["ts"]:
            grouped["ts"] = record.ts

        grouped["message_groups"][record.group_id][record.text_sms] += 1

    # Paging
    sdt_list = list(grouped_data.items())
    total = len(sdt_list)
    start = page * page_size
    end = start + page_size
    paginated = sdt_list[start:end]

    # Format the result
    result = []
    for i, (sdt_in, data) in enumerate(paginated, start=start + 1):
        groups = []
        for group_id, messages in data["message_groups"].items():
            message_list = [MessageCount(text_sms=text, count=count) for text, count in messages.items()]
            groups.append(GroupMessages(group_id=group_id, messages=message_list))

        result.append(SMSGroupedData(
            stt=i,
            sdt_in=sdt_in,
            frequency=data["frequency"],
            ts=data["ts"].isoformat() if isinstance(data["ts"], datetime) else str(data["ts"]),
            message_groups=groups
        ))

    # Check if the current page exceed the total pages
    total_pages = ceil(total/page_size)
    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )

    return BasePaginatedResponseContent(
        status_code=200,
        message="Success",
        data=result,
        error=False,
        error_message="",
        page=page,
        limit=page_size,
        total=total
    )


