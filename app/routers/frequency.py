from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, update, and_, func
from app.db import get_session
from app.models import SMS_Data
from app.schemas import *
from app.utils import *
from app.config import settings
from datetime import datetime
import csv
from collections import defaultdict
import io

router = APIRouter(
    prefix="/frequency",
    tags=['Frequency']
)


@router.get("/")
async def get_spam_base_on_frequency(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None
) -> BasePaginatedResponseFrequency:
    
    # --- Time validation ---
    from_datetime, to_datetime = validate_time_range(session, from_datetime, to_datetime)

    # --- Base filters ---
    filters = [SMS_Data.ts.between(from_datetime, to_datetime)]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))

    # --- Base grouped subquery (no offset/limit here) ---
    base_grouped_subq = (
        select(
            SMS_Data.group_id,
            func.min(SMS_Data.ts).label("first_ts"),
            func.count().label("frequency")
        )
        .where(*filters)
        .group_by(SMS_Data.group_id)
        .having(func.count() >= 20)
        .subquery()
    )

    # --- Count total records ---
    total_records = session.exec(
        select(func.count()).select_from(base_grouped_subq)
    ).one()
    total_pages = (total_records + page_size - 1) // page_size

    if total_records == 0:
        return BasePaginatedResponseFrequency(
            status_code=200,
            message="No data found",
            data=[],
            error=False,
            error_message="",
            page=page,
            limit=page_size,
            total=0
        )

    if page >= total_pages:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Page {page} exceeds total pages ({total_pages})",
                "page": page,
                "limit": page_size,
                "total": total_records
            }
        )

    # --- Paginated subquery ---
    paginated_subq = (
        select(
            base_grouped_subq.c.group_id,
            base_grouped_subq.c.first_ts,
            base_grouped_subq.c.frequency,
        )
        .order_by(base_grouped_subq.c.first_ts)
        .offset(page * page_size)
        .limit(page_size)
        .subquery()
    )

    # --- Join back to get agg_message ---
    grouped_stmt = (
        select(
            paginated_subq.c.group_id,
            paginated_subq.c.first_ts,
            paginated_subq.c.frequency,
            SMS_Data.text_sms.label("agg_message")
        )
        .join(
            SMS_Data,
            and_(
                SMS_Data.group_id == paginated_subq.c.group_id,
                SMS_Data.ts == paginated_subq.c.first_ts
            )
        )
        .order_by(paginated_subq.c.first_ts)
    )
    grouped_records = session.exec(grouped_stmt).all()

    # --- Collect IDs for second query ---
    group_ids = [r.group_id for r in grouped_records]

    # --- Second query: all messages for these groups ---
    msg_stmt = (
        select(
            SMS_Data.group_id,
            SMS_Data.text_sms,
            func.count().label("count")
        )
        .where(
            SMS_Data.group_id.in_(group_ids),
            SMS_Data.ts.between(from_datetime, to_datetime)  # only time filter
        )
        .group_by(SMS_Data.group_id, SMS_Data.text_sms)
    )
    all_messages = session.exec(msg_stmt).all()

    # --- Map messages ---
    messages_dict = defaultdict(list)
    for m in all_messages:
        messages_dict[m.group_id].append(
            MessageCount(text_sms=m.text_sms, count=m.count)
        )

    # --- Build result ---
    start_index = page * page_size + 1
    result = [
        SMSGroupedFrequency(
            stt=i,
            group_id=r.group_id,
            frequency=r.frequency,
            ts=r.first_ts,
            agg_message=r.agg_message,
            messages=messages_dict.get(r.group_id, [])
        )
        for i, r in enumerate(grouped_records, start=start_index)
    ]

    return BasePaginatedResponseFrequency(
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
async def export_frequency_data(
    session: Annotated[Session, Depends(get_session)],
    from_datetime: Annotated[datetime, Query(description="Time Start: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    to_datetime: Annotated[datetime, Query(description="Time End: (format: YYYY-MM-DD HH:MM:SS)")] = None,
    text_keyword: Annotated[str, Query(description="Filter messages that contain this keyword (case insensitive)")] = None
):
    # Time validation
    from_datetime, to_datetime = validate_time_range(session, from_datetime, to_datetime)

    # Create all the filter needed
    filters = [SMS_Data.ts.between(from_datetime, to_datetime)]
    if text_keyword:
        filters.append(SMS_Data.text_sms.ilike(f"%{text_keyword}%"))

    # Build WHERE clause & params
    where_parts = ["ts BETWEEN %s AND %s"]
    params = [from_datetime, to_datetime]

    if text_keyword:
        where_parts.append("text_sms ILIKE %s")
        params.append(f"%{text_keyword}%")

    where_clause = " AND ".join(where_parts)

    # Final SQL 
    sql = f"""
        SELECT 
            group_id,
            COUNT(*) AS frequency,
            MIN(ts) AS first_ts,
            ARRAY_AGG(text_sms ORDER BY ts)[1] AS agg_message
        FROM {settings.TABLE_NAME}
        WHERE {where_clause}
        GROUP BY group_id;
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
        writer.writerow(["group_id", "frequency", "first_ts", "agg_message"])
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
        headers={"Content-Disposition": "attachment; filename=frequency_export.csv"}
    )


@router.put("/")
async def feedback_base_on_frequency(
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
