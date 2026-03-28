# Feature: F003
# Scenario: SC005
# Badge Model

from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    criteria = Column(Text, nullable=False)
    icon_url = Column(String, nullable=True)
