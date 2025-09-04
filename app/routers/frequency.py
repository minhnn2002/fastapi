from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, update, and_, or_
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import aliased
from math import ceil
from pandas import DataFrame
from collections import defaultdict
import io

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
    # Get min/max timestamps
    min_ts, max_ts = session.exec(
        select(func.min(SMS_Data.ts), func.max(SMS_Data.ts))
    ).one()

    from_datetime = from_datetime or min_ts
    to_datetime = to_datetime or max_ts

    if to_datetime < from_datetime:
        raise HTTPException(
            status_code=400,
            detail="'to_datetime' is earlier than 'from_datetime'."
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

    # Subquery: find first_ts and count for each group_id
    subq = (
        select(
            SMS_Data.group_id,
            func.min(SMS_Data.ts).label("first_ts"),
            func.count().label("frequency")
        )
        .where(*filters)
        .group_by(SMS_Data.group_id)
        .subquery()
    )

    # Check where the page exceeds or not
    total = session.exec(select(func.count()).select_from(subq)).one()
    total_pages = ceil(total / page_size)
    if page >= total_pages:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Page {page} exceeds total pages ({total_pages})",
                "page": page,
                "limit": page_size,
                "total": total
            }
    )

    # The agg query
    alias_sms = aliased(SMS_Data)
    stmt = (
        select(
            subq.c.group_id,
            subq.c.frequency,
            subq.c.first_ts,
            alias_sms.text_sms.label("agg_message")
        )
        .join(
            alias_sms,
            (alias_sms.group_id == subq.c.group_id)
            & (alias_sms.ts == subq.c.first_ts)
        )
        .order_by(subq.c.first_ts, subq.c.group_id)
        .offset(page * page_size)
        .limit(page_size)
    )
    grouped_records = session.exec(stmt).all()


    # Extract all the message in group
    group_filters = [
        and_(SMS_Data.group_id == record.group_id)
        for record in grouped_records
    ]

    msg_stmt = (
        select(
            SMS_Data.group_id,
            SMS_Data.text_sms,
            func.count().label("count")
        )
        .where(
            or_(*group_filters),  
            *filters              
        )
        .group_by(SMS_Data.group_id, SMS_Data.text_sms)
    )
    all_messages = session.exec(msg_stmt).all()

    messages_dict = defaultdict(list)
    for m in all_messages:
        messages_dict[m.group_id].append(
            MessageCount(text_sms=m.text_sms, count=m.count)
        )

    # Build result
    result = []
    for i, record in enumerate(grouped_records, start=page * page_size + 1):
        result.append(
            SMSGroupedFrequency(
                stt=i,
                group_id=record.group_id,
                frequency=record.frequency,
                ts=record.first_ts.isoformat(),
                agg_message=record.agg_message,
                messages=messages_dict.get(record.group_id, [])
            )
        )

    return BasePaginatedResponseFrequency(
        status_code=200,
        message="Success",
        data=result,
        error=False,
        error_message="",
        page=page,
        limit=page_size,
        total=total
    )

@router.get("/export")
def export_frequency_data(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    # Time validation
    min_ts = session.exec(select(func.min(SMS_Data.ts))).one()
    max_ts = session.exec(select(func.max(SMS_Data.ts))).one()

    if from_datetime is None and to_datetime is None:
        to_datetime = max_ts
        from_datetime = to_datetime - timedelta(hours=1)
    else:
        if from_datetime is None:
            from_datetime = to_datetime - timedelta(hours=1)

        if to_datetime is None:
            to_datetime = from_datetime + timedelta(hours=1)

        if to_datetime < from_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time range: 'to_datetime' is earlier than 'from_datetime'."
            )

        if to_datetime - from_datetime > timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time range cannot exceed 1 hour."
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

    subq = (
        select(
            SMS_Data.group_id,
            func.count().over(
                partition_by=SMS_Data.group_id
            ).label("frequency"),
            func.first_value(SMS_Data.text_sms).over(
                partition_by=SMS_Data.group_id,
                order_by=[SMS_Data.ts.asc(), SMS_Data.id.asc()]
            ).label("first_message"),
            func.min(SMS_Data.ts).over(
                partition_by=SMS_Data.group_id
            ).label("first_ts"),
            func.row_number().over(
                partition_by=SMS_Data.group_id,
                order_by=[SMS_Data.ts.asc(), SMS_Data.id.asc()]
            ).label("rn")
        )
        .where(*filters)
        .subquery()
    )

    # Lấy kết quả cuối cùng (chỉ rn=1)
    stmt = select(
        subq.c.group_id,
        subq.c.frequency,
        subq.c.first_message,
        subq.c.first_ts
    ).where(subq.c.rn == 1)

    result = session.exec(stmt).all()
    df = DataFrame(result, columns=["group_id", "frequency", "first_message", "first_ts"])

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=frequency_export.csv"
    return response


@router.put("/")
def feedback_base_on_frequency(
    session: Annotated[Session, Depends(get_session)],
    user_feedback: FrequencyFeedback
):

    stmt = (
        update(SMS_Data)
        .where(
            SMS_Data.group_id == user_feedback.group_id
        )
        .values(feedback=user_feedback.feedback)
    )
    result = session.exec(stmt)

    # Check the result if it is None
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="No records matched your condition"
        )

    session.commit()

    return BaseResponse(
        status_code = status.HTTP_200_OK,
        message = f"Updated {result.rowcount} records",
        error = False,
        error_message = None
    ) 
