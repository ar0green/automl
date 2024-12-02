# models.py

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    task_id = Column(String, unique=True, index=True)
    dataset_name = Column(String)
    model_name = Column(String)
    status = Column(String)
    report_data = Column(JSON)
    mlflow_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
