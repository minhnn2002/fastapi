from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class Content_Feedback(BaseModel):
    sdt_in: str
    group_id: str
    ts: datetime
    feedback: Literal[0, 1]

