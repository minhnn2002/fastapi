from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, update
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import defaultdict
from math import ceil
from pandas import DataFrame
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
    stmt = (
        select(
            SMS_Data.group_id,
            SMS_Data.sdt_in,
            SMS_Data.ts,
            SMS_Data.text_sms,
            func.count().over(
                partition_by=SMS_Data.group_id
            ).label("frequency"),
            func.first_value(SMS_Data.text_sms).over(
                partition_by=SMS_Data.group_id,
                order_by=[SMS_Data.ts.asc(), SMS_Data.id.asc()]
            ).label("first_message"),
            func.min(SMS_Data.ts).over(
                partition_by=SMS_Data.group_id
            ).label("first_ts")
        )
        .where(*filters) 
    )

    records = session.exec(stmt).all()    

    grouped_data = defaultdict(lambda: {
        "frequency": None,
        "ts": None,
        "agg_message": None,
        "messages": []
    })

    for record in records:
        key = record.group_id
        grouped = grouped_data[key]
        grouped['frequency'] = record.frequency
        grouped['ts'] = record.first_ts
        grouped["agg_message"] = record.first_message
        
        # Kiểm tra xem message đã tồn tại chưa
        found = None
        for m in grouped["messages"]:
            if m["text_sms"] == record.text_sms:
                found = m
                break

        if found:
            # Nếu đã tồn tại thì tăng count
            found["count"] += 1
        else:
            # Nếu chưa thì thêm mới
            grouped["messages"].append({
                "text_sms": record.text_sms,
                "count": 1
            })

    # Paging
    group_list = list(grouped_data.items())
    total = len(group_list)
    start = page * page_size
    end = start + page_size
    paginated = group_list[start:end]

    # Format the result
    result = []
    for i, (group_id, data) in enumerate(paginated, start=start + 1):
        message_list = [MessageCount(text_sms=m["text_sms"], count=m["count"]) for m in data["messages"]]
        result.append(SMSGroupedFrequency(
            stt=i,
            group_id=group_id,
            frequency=data["frequency"],
            ts=data["ts"].isoformat() if isinstance(data["ts"], datetime) else str(data["ts"]),
            agg_message=data["agg_message"],
            messages=message_list
        ))

    # Check if the current page exceed the total pages
    total_pages = ceil(total/page_size)
    if page > total_pages:
        raise HTTPException(
            status_code=400,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )


    return BasePaginatedResponseFrequency(
        status_code=status.HTTP_200_OK,
        message="Success",
        data=result,
        error=False,
        error_message="",
        page=page,
        limit=page_size,
        total=total_pages
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
            from_datetime = max(to_datetime - timedelta(hours=1), min_ts)

        if to_datetime is None:
            to_datetime = min(from_datetime + timedelta(hours=1), max_ts)

        # Validate only if user explicitly sets values
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
            SMS_Data.group_id == user_feedback.group_id,
            SMS_Data.text_sms == user_feedback.text_sms
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
