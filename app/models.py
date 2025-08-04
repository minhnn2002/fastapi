from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class SMS_Data(SQLModel, table=True):
    __tablename__ = "demo"  

    ts: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True}, primary_key=True)
    sdt_in: Optional[str] = Field(default=None, max_length=100, primary_key=True)
    group_id: Optional[str] = Field(default=None, max_length=100)
    sdt_out: Optional[str] = Field(default=None, max_length=100)
    text_sms: Optional[str] = Field(default=None, max_length=500, primary_key=True)
    id: Optional[str] = Field(default=None, primary_key=True, max_length=100)
    predicted_label: Optional[str] = Field(default=None, max_length=100)
    confidence: Optional[str] = Field(default=None, max_length=100)
    feedback: Optional[int] = Field(default=None)
