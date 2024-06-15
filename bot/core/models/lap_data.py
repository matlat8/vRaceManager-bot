from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ARRAY

Base = declarative_base()

class LapData(Base):
    __tablename__ = 'lap_data'
    id = Column(Integer, primary_key=True)
    subsession_id = Column(Integer)
    simsession_number = Column(Integer)
    group_id = Column(Integer)
    lap_number = Column(Integer)
    cust_id = Column(Integer)
    display_name = Column(String)
    flags = Column(Integer)
    incident = Column(Boolean)
    session_time = Column(Integer)
    lap_time = Column(Integer)
    lap_events = Column(ARRAY(String))
    lap_position = Column(Integer)
    interval = Column(Integer)
    fastest_lap = Column(Boolean)
    created_at = Column(TIMESTAMP)