from datetime import date

from sqlalchemy import Column, Date, Integer, String, Text

from .db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company = Column(String(120), nullable=False)
    role = Column(String(120), nullable=False)
    status = Column(String(20), nullable=False, default="applied")
    applied_on = Column(Date, nullable=False, default=date.today)
    notes = Column(Text, nullable=False, default="")
