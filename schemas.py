from pydantic import BaseModel

# Схема для создания курса
class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    is_paid: bool = False
    price: int = 0

# Схема для ответа (с ID)
class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_paid: bool
    price: int

    class Config:
        orm_mode = True  # Для работы с SQLAlchemy объектами