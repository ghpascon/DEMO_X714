from sqlalchemy import Column, Integer, String, DateTime
from app.db.session import Base

class DbTag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime)                   
    epc = Column(String(50))             
    tid = Column(String(50))
    ant = Column(Integer)
    rssi = Column(Integer)
    card_id = Column(String(50))             
    door = Column(String(10))             
