from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy import func

def validate_time_range(
    session,
    from_datetime: datetime | None,
    to_datetime: datetime | None,
):
    """
    Validate and normalize a time range:
    - Default: last `max_hours` if both None.
    - Not exceed `max_hours`.
    - `to_datetime` <= now.
    - `from_datetime` >= min(ts) in DB.
    """

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

    return from_datetime, to_datetime
