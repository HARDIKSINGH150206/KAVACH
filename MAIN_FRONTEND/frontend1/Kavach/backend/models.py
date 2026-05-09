from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from .database import Base

class PatientSession(Base):
    __tablename__ = "patient_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    symptoms = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    severity_level = Column(Integer, nullable=False) # 1 to 5
    recommended_action = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
