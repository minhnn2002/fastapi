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
    page_size: Annotated[int, Query(description="The number of record in one page", enum=[10, 50, 100])] = 10
):
    
    # If datetime is not specified then use every date
    min_datetime = session.exec(select(func.min(Spam_Info.ts))).one()
    max_datetime = session.exec(select(func.max(Spam_Info.ts))).one()
    if from_datetime is None or from_datetime < min_datetime:
        from_datetime = min_datetime
    if to_datetime is None or to_datetime > max_datetime:
        to_datetime = max_datetime

    # SQL query to calculate total rows
    base_query = (
        select(
            Spam_Info.sdt_in,
            Spam_Info.text_sms,
            func.count().label("frequency"),
            Spam_Info.ts
        )
        .where(Spam_Info.ts >= from_datetime)
        .where(Spam_Info.ts <= to_datetime)
        .group_by(Spam_Info.sdt_in, Spam_Info.text_sms, Spam_Info.ts)
    )

    sub = base_query.subquery()
    total_rows = session.exec(select(func.count()).select_from(sub)).one()
    total_pages = ceil(total_rows/page_size)

    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page {page} exceeds total pages ({total_pages})"
    )

    
    # Calculate the offset and query with the offset 
    offset = (page - 1) * page_size
    paginated_query = base_query.offset(offset).limit(page_size).order_by(Spam_Info.ts, desc(column("frequency")))
    records = session.exec(paginated_query).all()

    return [
        {"stt": i + 1 + offset, **dict(r._mapping)}
        for i, r in enumerate(records)
    ]

# @router.put("/")
# def feedback_spam_base_on_content(
#     session: Annotated[Session, Depends(get_session)],
#     user_feedback: Content_Feedback
# ):
    # query = select(Spam_Info).where(
    #     (Spam_Info.sdt_in == user_feedback.sdt_in) &
    #     (Spam_Info.ts == user_feedback.ts) &
    #     (Spam_Info.text_sms == user_feedback.sms_text)
    # )
    
    # records = session.exec(query).all()
    # if not records:
    #     raise HTTPException(status_code=404, detail="No matching records found")

    # feedback_data = user_feedback.model_dump(exclude_unset=True)
    # for record in records:
    #     record.update(feedback_data)
    #     session.add(record)
    #     # session.commit()
    #     session.refresh(record)
    # return {"message": "Update success"}

    # check_query = """
    #     SELECT 1 FROM demo WHERE ts = :ts AND sdt_in = :sdt_in AND group_id = :group_id
    # """
    # insert_query = """
    #     INSERT INTO demo (ts, sdt_in, group_id, feedback)
    #     VALUES (:ts, :sdt_in, :group_id, :feedback)
    # """
    # params = {
    #     "ts": user_feedback.ts,
    #     "sdt_in": user_feedback.sdt_in,
    #     "group_id": user_feedback.group_id
    # }

    # tmp = session.exec("SELECT column_name FROM information_schema.columns WHERE table_name = 'demo'").all()
    # columns = [row[0] for row in tmp]

    # try:
    #     # Check the existence of the record
    #     result = session.exec(text(check_query), params = params).fetchone()
    #     if not result:
    #         raise HTTPException(status_code=404, detail="Record not found")

    #     # Update the record
    #     session.exec(text(insert_query), params = params)
    #     # session.commit()
    #     return {"message": "Record updated successfully"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



