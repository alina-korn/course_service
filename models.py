from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_paid = Column(Boolean, default=False)  # Платный или бесплатный
    price = Column(Integer, default=0)        # Цена в условных единицах (если платный)