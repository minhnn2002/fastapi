from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func, and_, update, or_, case, text, tuple_
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from app.utils import *
from app.config import settings
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
    from_datetime: Annotated[str, Query(description="Time Start: (ISO format)")] = None,
    to_datetime: Annotated[str, Query(description="Time End: (ISO format)")] = None,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
) -> BasePaginatedResponseContent:
    
    # --- Parse time string ---
    from_datetime = parse_datetime(from_datetime)
    to_datetime = parse_datetime(to_datetime)
    # --- Time validation ---
    from_datetime, to_datetime = validate_time_range(session, from_datetime, to_datetime)

    # --- Base filters ---
    filters = [SMS_Data.ts.between(from_datetime, to_datetime)]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))
    if phone_num:
        filters.append(SMS_Data.sdt_in.ilike(f"%{phone_num}%"))

    # --- Aggregation query ---
    agg_query = (
        select(
            SMS_Data.group_id,
            SMS_Data.sdt_in,
            func.min(SMS_Data.ts).label("first_ts"),
            func.count().label("frequency"),
            func.min_by(SMS_Data.text_sms, SMS_Data.ts).label("agg_message")
        )
        .where(*filters)
        .group_by(SMS_Data.group_id, SMS_Data.sdt_in)
        .having(func.count() >= 20)
        .subquery()
    )

    # --- Pagination query ---
    main_stmt = (
        select(
            agg_query.c.group_id,
            agg_query.c.sdt_in,
            agg_query.c.first_ts,
            agg_query.c.frequency,
            agg_query.c.agg_message,
            func.count().over().label("total_records")
        )
        .order_by(agg_query.c.first_ts, agg_query.c.group_id, agg_query.c.sdt_in)
        .offset(page * page_size)
        .limit(page_size)
    )
    grouped_records = session.exec(main_stmt).all()
    total_records = grouped_records[0].total_records if grouped_records else 0

    # --- Second query: all messages ---
    group_ids = [r.group_id for r in grouped_records]
    phone_numbers = [r.sdt_in for r in grouped_records]

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

    # --- Build message dictionary ---
    messages_dict = defaultdict(list)
    for m in all_messages:
        messages_dict[(m.group_id, m.sdt_in)].append(
            MessageCount(text_sms=m.text_sms, count=m.count)
        )

    # --- Build result ---
    start_index = page * page_size + 1
    result = [
        SMSGroupedContent(
            stt=i,
            group_id=r.group_id,
            sdt_in=r.sdt_in,
            frequency=r.frequency,
            ts=r.first_ts,
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
        total=total_records
    )


@router.get("/export")
async def export_content_data(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[str, Query(description="Time Start: (ISO format)")] = None,
    to_datetime: Annotated[str, Query(description="Time End: (ISO format)")] = None,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None,
    phone_num: Annotated[str, Query(description="Filter phone number that contain this pattern (case insensitive)")] = None
):
    
    # --- Parse time string ---
    from_datetime = parse_datetime(from_datetime)
    to_datetime = parse_datetime(to_datetime)

    # --- Time validation ---
    from_datetime, to_datetime = validate_time_range(session, from_datetime, to_datetime)

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
def feedback_base_on_content(
    user_feedback: list[ContentFeedback],
    session: Session = Depends(get_session),
    
):
    total_updated = 0

    for item in user_feedback:
        stmt = (
            update(SMS_Data)
            .where(
                SMS_Data.group_id == item.group_id,
                SMS_Data.sdt_in == item.sdt_in
            )
            .values(feedback=item.feedback)
        )
        result = session.exec(stmt)
        total_updated += result.rowcount

    session.commit()

    if total_updated == 0:
        raise HTTPException(status_code=404, detail="No records matched your condition")

    return BaseResponse(
        status_code=status.HTTP_200_OK,
        message=f"Updated {total_updated} records",
        error=False,
        error_message=None
    )

@router.put("/")
def feedback_base_on_content(
    user_feedback: list[ContentFeedback],
    session: Session = Depends(get_session),
    
):
    total_updated = 0

    for item in user_feedback:
        stmt = (
            update(SMS_Data)
            .where(
                SMS_Data.group_id == item.group_id,
                SMS_Data.sdt_in == item.sdt_in
            )
            .values(feedback=item.feedback)
        )
        result = session.exec(stmt)
        total_updated += result.rowcount

    session.commit()

    if total_updated == 0:
        raise HTTPException(status_code=404, detail="No records matched your condition")

    return BaseResponse(
        status_code=status.HTTP_200_OK,
        message=f"Updated {total_updated} records",
        error=False,
        error_message=None
    )