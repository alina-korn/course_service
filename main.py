from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Course, Base
from schemas import CourseCreate, CourseResponse

app = FastAPI(title="Course Service")

# Создание таблиц в БД при запуске
Base.metadata.create_all(bind=engine)

# Создание нового курса
@app.post("/courses/", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
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

# Получение списка всех курсов
@app.get("/courses/", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses

# Получение курса по ID
@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)