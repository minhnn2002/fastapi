from typing import Optional
from datetime import datetime
from typing import Annotated
from sqlmodel import Field, SQLModel


class Spam_Info(SQLModel, table=True):
    __tablename__ = "dev_demo4"  

    ts: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})
    sdt_in: Optional[str] = Field(default=None, max_length=100)
    group_id: Optional[str] = Field(default=None, max_length=100)
    sdt_out: Optional[str] = Field(default=None, max_length=100)
    text_sms: Optional[str] = Field(default=None, max_length=500)
    id: Optional[str] = Field(default=None, primary_key=True, max_length=100)
    predicted_label: Optional[str] = Field(default=None, max_length=100)
    confidence: Optional[str] = Field(default=None, max_length=100)
    feedback: Optional[int] = Field(default=None)
