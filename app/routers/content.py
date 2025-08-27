from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlmodel import Session, select, func, update, case
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
    min_ts = session.exec(select(func.min(SMS_Data.ts))).one()
    max_ts = session.exec(select(func.max(SMS_Data.ts))).one()

    if from_datetime is None and to_datetime is None:
        from_datetime, to_datetime = min_ts, max_ts
    else:
        if from_datetime is None:
            from_datetime = min_ts
        if to_datetime is None:
            to_datetime = max_ts

        # Only validate if user explicitly set something
        if from_datetime < min_ts or to_datetime > max_ts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Time range must be within [{min_ts}, {max_ts}]"
            )

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


    # Filter 
    filtered_cte = (
        select(
            SMS_Data.group_id,
            SMS_Data.sdt_in,
            SMS_Data.ts,
            SMS_Data.text_sms,
            func.row_number().over(
                partition_by=SMS_Data.group_id,
                order_by=[SMS_Data.ts.asc(), SMS_Data.id.asc()]
            ).label("rn"),
            func.count().over(partition_by=SMS_Data.group_id).label("frequency")
        )
        .where(*filters)  # filter nếu có
        .cte("filtered_cte")
    )

    # 
    query = (
        select(
            filtered_cte.c.group_id,
            filtered_cte.c.sdt_in,
            filtered_cte.c.ts,
            filtered_cte.c.text_sms,
            filtered_cte.c.frequency,
            case((filtered_cte.c.rn == 1, True), else_=False).label("is_first")
        )
    )

    records = session.exec(query).all()

    grouped_data = defaultdict(lambda: {
        "frequency": None,
        "ts": None,
        "agg_message": None,
        "phones": defaultdict(lambda: defaultdict(int))
    })

    for record in records:
        grouped = grouped_data[record.group_id]
        grouped['frequency'] = record.frequency
        grouped['ts'] = record.ts
        if record.is_first is True:
            grouped['agg_message'] = record.text_sms
        grouped["phones"][record.sdt_in][record.text_sms] += 1

    # Paging
    group_list = list(grouped_data.items())
    total = len(group_list)
    start = page * page_size
    end = start + page_size
    paginated = group_list[start:end]

    # Format the result
    result = []
    for i, (group_id, data) in enumerate(paginated, start=start + 1):
        groups = []
        for sdt_in, messages in data["phones"].items():
            message_list = [MessageCount(text_sms=text, count=count) for text, count in messages.items()]
            groups.append(PhoneMessages(sdt_in=sdt_in, messages=message_list))

        result.append(SMSGroupedData(
            stt=i,
            group_id=group_id,
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


# If any message is marked as spam, then all the messages belong to the same group will be marked as spam
@router.put("/")
def feedback_base_on_content(
    session: Annotated[Session, Depends(get_session)],
    user_feedback: ContentFeedback
):
    filters = [
        SMS_Data.sdt_in == user_feedback.sdt_in,
        SMS_Data.text_sms == user_feedback.text_sms
    ]

    # Retrieve the group_id of the spammed message
    group_id = session.exec(select(SMS_Data.group_id).where(*filters)).one()

    if not group_id:
        raise HTTPException(
            status_code=404,
            detail="Records are not found"
        )

    # Mark all the group as spam
    stmt = (
        update(SMS_Data)
        .where(SMS_Data.group_id == group_id)
        .values(feedback=user_feedback.feedback)
    )

    result = session.exec(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Records are not found"
        )

    session.commit()

    return {
        "Message": f"Updated {result.rowcount} records",
    }


