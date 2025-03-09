from pydantic import BaseModel, EmailStr

# Схемы для курсов (как было)
class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    is_paid: bool = False
    price: int = 0

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_paid: bool
    price: int

    class Config:
        orm_mode = True

# Схемы для пользователей и авторизации
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str