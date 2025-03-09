from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Course, User, Base
from schemas import CourseCreate, CourseResponse, UserCreate, UserResponse, Token
from auth import (
    create_access_token, authenticate_user, get_current_user, oauth,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
)
from starlette.responses import RedirectResponse

app = FastAPI(title="Course Service")

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Регистрация пользователя
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Вход через email/пароль
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Вход через Google (инициация)
@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Callback для Google OAuth
@app.get("/auth/google", response_model=Token)
async def auth_google(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Google auth failed")
    
    email = user_info["email"]
    db_user = get_user_by_email(db, email)
    if not db_user:
        db_user = User(email=email, hashed_password=None)  # Без пароля для OAuth
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}

# Создание курса (только авторизованные)
@app.post("/courses/", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_course = Course(
        title=course.title,
        description=course.description,
        is_paid=course.is_paid,
        price=course.price if course.is_paid else 0
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Получение списка курсов (доступно всем)
@app.get("/courses/", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses

# Получение курса по ID (доступно всем)
@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)