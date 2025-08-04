from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class MessageCount(BaseModel):
    text_sms: str
    count: int

class GroupMessages(BaseModel):
    group_id: str
    messages: list[MessageCount]

class BaseData(BaseModel):
    stt: int
    sdt_in: str
    frequency: int
    ts: datetime

class SMSGroupedData(BaseData):
    message_groups: list[GroupMessages]

class BaseResponse(BaseModel):
    status_code: int
    message: str|None = None
    error: bool = False
    error_message: str|None = None


class BasePaginatedResponseContent(BaseResponse):
    data: list[SMSGroupedData]|None = None
    page: int
    limit: int
    total: int

class BasePaginatedResponseFrequency(BaseResponse):
    data: list[BaseData]
    page: int
    limit: int
    total: int
