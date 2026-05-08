# Feature: Dashboard
# Traceability: Infrastructure

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ProductEvent(Base):
    __tablename__ = "product_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    player_id = Column(Integer, nullable=True)
    metadata_json = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
