from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Out(BaseModel):
    ts: Optional[datetime]
    sdt_in: Optional[str]
    group_id: Optional[str]
    sdt_out: Optional[str]
    text_sms: Optional[str]
    id: Optional[str]
    predicted_label: Optional[str]
    confidence: Optional[str]
    feedback: Optional[int]
