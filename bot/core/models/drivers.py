from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    iracing_id = Column(Integer)
    discord_id = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    notifications_enabled = Column(Boolean)
    


    def __repr__(self):
        return f"<Driver(name='{self.name}', age={self.age}, team='{self.team}', country='{self.country}')>"