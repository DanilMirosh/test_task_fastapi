from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    access_token = Column(String, unique=True, index=True)


class AudioRecord(Base):
    __tablename__ = 'audio_records'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    record_id = Column(String, unique=True, index=True)
    download_url = Column(String, unique=True, index=True)
