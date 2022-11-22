from sqlalchemy import Column, Integer, Float, String
from .database import Base



class AddreBook(Base):
    __tablename__ = 'addrbook'

    id = Column(Integer, primary_key=True, index=True)
    place = Column(String,nullable= True)
    lat = Column(Float)
    lng = Column(Float)