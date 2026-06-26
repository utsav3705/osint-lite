"""
OSINT-Pro — ORM Models
SQLAlchemy models for the investigations database.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from database import Base


class Investigation(Base):
    """Represents a single OSINT investigation case."""

    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_name = Column(String(255), nullable=False, index=True)
    username = Column(String(255), default="")
    email = Column(String(255), default="")
    company = Column(String(255), default="", index=True)
    website = Column(String(255), default="")
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    risk_score = Column(Float, default=0.0)
    risk_classification = Column(String(20), default="Low")
    report_path = Column(String(512), default="")
    analyst = Column(String(100), default="analyst")
    status = Column(String(50), default="Completed")
    notes = Column(Text, default="")

    def __repr__(self):
        return (
            f"<Investigation(id={self.id}, subject='{self.subject_name}', "
            f"risk={self.risk_score}, status='{self.status}')>"
        )

    def to_dict(self):
        """Serialise the record to a plain dictionary."""
        return {
            "id": self.id,
            "subject_name": self.subject_name,
            "username": self.username,
            "email": self.email,
            "company": self.company,
            "website": self.website,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M") if self.date_created else "",
            "risk_score": self.risk_score,
            "risk_classification": self.risk_classification,
            "report_path": self.report_path,
            "analyst": self.analyst,
            "status": self.status,
            "notes": self.notes,
        }
