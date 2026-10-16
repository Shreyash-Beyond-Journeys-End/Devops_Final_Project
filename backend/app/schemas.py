from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

STATUSES = ["applied", "interview", "offer", "rejected"]
Status = Literal["applied", "interview", "offer", "rejected"]


# what the client sends when creating or updating a job
class JobIn(BaseModel):
    company: str = Field(max_length=120)
    role: str = Field(max_length=120)
    status: Status = "applied"
    applied_on: date = Field(default_factory=date.today)
    notes: str = ""

    # company and role should not be empty or only spaces
    @field_validator("company", "role")
    @classmethod
    def check_not_blank(cls, value):
        value = value.strip()
        if value == "":
            raise ValueError("cannot be empty")
        return value


# what the api sends back
class JobOut(JobIn):
    id: int

    model_config = {"from_attributes": True}


class Stats(BaseModel):
    total: int
    applied: int
    interview: int
    offer: int
    rejected: int
