from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class SMS_Data(SQLModel, table=True):
    __tablename__ = "demo"  

    id: str = Field(primary_key=True, max_length=100)
    ts: datetime = Field(primary_key=True)
    sdt_in: str = Field(primary_key=True, max_length=100)
    group_id: str = Field(primary_key=True, max_length=100)

    sdt_out: Optional[str] = Field(default=None, max_length=100)
    text_sms: Optional[str] = Field(default=None, max_length=500)
    predicted_label: Optional[str] = Field(default=None, max_length=100)
    llm_label: Optional[str] = Field(default=None, max_length=100)
    confidence: Optional[str] = Field(default=None, max_length=100)
    feedback: Optional[bool] = Field(default=None)
