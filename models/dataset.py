import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship

from db.database import Base


class DataSetMeta(Base):
    __tablename__ = 'datasetmeta'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='datasetmeta')
