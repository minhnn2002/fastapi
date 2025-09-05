from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func, update, and_
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from app.config import settings
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import io


router = APIRouter(
    prefix="/content",
    tags=['Content']
)


@router.get("/")
async def get_spam_base_on_content(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
) -> BasePaginatedResponseContent:
    DEFAULT_FROM_DATETIME = datetime(1900, 1, 1)  
    DEFAULT_TO_DATETIME = datetime.now()

    # Default range handling
    from_datetime = from_datetime or DEFAULT_FROM_DATETIME
    to_datetime = to_datetime or DEFAULT_TO_DATETIME

    # Only validate if user explicitly set something
    if to_datetime < from_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time range: 'to_datetime' is earlier than 'from_datetime'."
        )

    # Build base filters
    filters = [SMS_Data.ts.between(from_datetime, to_datetime)]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))
    if phone_num:
        filters.append(SMS_Data.sdt_in.ilike(f"%{phone_num}%"))

    # Count total records for pagination
    total = session.scalar(
        select(func.count()).select_from(
            select(SMS_Data.group_id, SMS_Data.sdt_in)
            .distinct()
            .where(*filters)
            .subquery()
        )
    )

    total_pages = (total + page_size - 1) // page_size
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

    # Subquery: get first_ts per group
    first_ts_subq = (
        select(
            SMS_Data.group_id,
            SMS_Data.sdt_in,
            func.min(SMS_Data.ts).label("first_ts"),
            func.count().label("frequency")
        )
        .where(*filters)
        .group_by(SMS_Data.group_id, SMS_Data.sdt_in)
        .order_by(func.min(SMS_Data.ts))
        .offset(page * page_size)
        .limit(page_size)
        .subquery()
    )

    # Join back to get the agg_message (first message per group)
    grouped_stmt = (
        select(
            first_ts_subq.c.group_id,
            first_ts_subq.c.sdt_in,
            first_ts_subq.c.first_ts,
            first_ts_subq.c.frequency,
            func.min(SMS_Data.text_sms).label("agg_message")
        )
        .join(
            first_ts_subq,
            and_(
                SMS_Data.group_id == first_ts_subq.c.group_id,
                SMS_Data.sdt_in == first_ts_subq.c.sdt_in,
                SMS_Data.ts == first_ts_subq.c.first_ts
            )
        )
        .group_by(first_ts_subq.c.group_id, first_ts_subq.c.sdt_in, first_ts_subq.c.first_ts, first_ts_subq.c.frequency)
        .order_by(first_ts_subq.c.first_ts)
    )
    grouped_records = session.exec(grouped_stmt).all()

    if not grouped_records:
        return BasePaginatedResponseContent(
            status_code=200,
            message="Success",
            data=[],
            error=False,
            error_message="",
            page=page,
            limit=page_size,
            total=total_pages
        )

    # Get all messages for these groups in one query
    group_ids = {r.group_id for r in grouped_records}
    phone_numbers = {r.sdt_in for r in grouped_records}

    msg_stmt = (
        select(
            SMS_Data.group_id,
            SMS_Data.sdt_in,
            SMS_Data.text_sms,
            func.count().label("count")
        )
        .where(
            SMS_Data.group_id.in_(group_ids),
            SMS_Data.sdt_in.in_(phone_numbers),
            *filters
        )
        .group_by(SMS_Data.group_id, SMS_Data.sdt_in, SMS_Data.text_sms)
    )
    all_messages = session.exec(msg_stmt).all()

    # Map messages
    messages_dict = defaultdict(list)
    for m in all_messages:
        messages_dict[(m.group_id, m.sdt_in)].append(
            MessageCount(text_sms=m.text_sms, count=m.count)
        )

    # Build result
    start_index = page * page_size + 1
    result = [
        SMSGroupedContent(
            stt=i,
            group_id=r.group_id,
            sdt_in=r.sdt_in,
            frequency=r.frequency,
            ts=r.first_ts.isoformat(),
            agg_message=r.agg_message,
            messages=messages_dict.get((r.group_id, r.sdt_in), [])
        )
        for i, r in enumerate(grouped_records, start=start_index)
    ]

    return BasePaginatedResponseContent(
        status_code=200,
        message="Success",
        data=result,
        error=False,
        error_message="",
        page=page,
        limit=page_size,
        total=total_pages
    )

@router.get("/export")
async def export_content_data(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    # Handle time range 
    if from_datetime is None and to_datetime is None: 
        to_datetime = session.exec(select(func.max(SMS_Data.ts))).one()
        from_datetime = to_datetime - timedelta(hours=1)
    else:
        if from_datetime is None:
            from_datetime = to_datetime - timedelta(hours=1)
        if to_datetime is None:
            to_datetime = from_datetime + timedelta(hours=1)

    if to_datetime < from_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'to_datetime' cannot be earlier than 'from_datetime'."
        )
    if to_datetime - from_datetime > timedelta(hours=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time range cannot exceed 1 hour."
        )

    # Create all the filter needed
    filters = [SMS_Data.ts.between(from_datetime, to_datetime)]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))
    if phone_num:
        filters.append(SMS_Data.sdt_in.ilike(f"%{phone_num}%"))

    # Build WHERE clause & params
    where_parts = ["ts BETWEEN %s AND %s"]
    params = [from_datetime, to_datetime]

    if text_keyword:
        where_parts.append("text_sms ILIKE %s")
        params.append(f"%{text_keyword}%")
    if phone_num:
        where_parts.append("sdt_in ILIKE %s")
        params.append(f"%{phone_num}%")

    where_clause = " AND ".join(where_parts)

    # Final SQL 
    sql = f"""
        SELECT 
            group_id,
            sdt_in,
            COUNT(*) AS frequency,
            MIN(ts) AS first_ts,
            ARRAY_AGG(text_sms ORDER BY ts)[1] AS agg_message
        FROM {settings.TABLE_NAME}
        WHERE {where_clause}
        GROUP BY group_id, sdt_in;
    """

    # Get raw connection & cursor
    connection = session.get_bind().raw_connection()
    cursor = connection.cursor()
    cursor.execute(sql, params)

    # Streaming generator
    def stream():
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)

        # Write header first
        writer.writerow(["group_id", "sdt_in", "frequency", "first_ts", "agg_message"])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        # Stream rows in chunks
        for rows in iter(lambda: cursor.fetchmany(50000), []):
            for row in rows:
                writer.writerow(row)
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            cursor.close()
            connection.close()

    # ---- Return streaming response ----
    return StreamingResponse(
        stream(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=content_export.csv"}
    )



@router.put("/")
async def feedback_base_on_content(
    session: Annotated[Session, Depends(get_session)],
    user_feedback: ContentFeedback
):
    stmt = (
        update(SMS_Data)
        .where(
            SMS_Data.group_id == user_feedback.group_id, 
            SMS_Data.sdt_in == user_feedback.sdt_in
        )
        .values(feedback=user_feedback.feedback)
    )

    result = session.exec(stmt)

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






