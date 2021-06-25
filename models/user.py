from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    datasetmeta = relationship('DataSetMeta', back_populates='user')
