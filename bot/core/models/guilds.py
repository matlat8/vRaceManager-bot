from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Guilds(Base):
    __tablename__ = 'guilds'
    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, unique=True)
    hosted_channel_id = Column(Integer)
    official_channel_id = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<Guilds(guild_id='{self.guild_id}', hosted_channel_id={self.hosted_channel_id}, official_channel_id={self.official_channel_id}, created_at={self.created_at}, updated_at={self.updated_at})>"