from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm.session import Session
from sqlalchemy import desc
from starlette import status

from app.logic.database import get_db
from app.models.models import TokenData
from app.schemas import schemas
from app.models import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, name=token_data.username)
    if user is None:
        raise credentials_exception
    return models.User(
        name=user.name, email=user.email, hashed_password=user.hashed_password
    )


def create_application(db: Session, internship: int, status: str,
                       user: models.User):
    user = get_user_by_username(name=user.name, db=db)
    db_application = schemas.Application(user_id=user.id, internship_id=internship,
                                         status=status)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def create_internship(db: Session, internship: models.Internship):
    db_internship = schemas.Internship(name=internship.name, description=internship.description,
                                       updated_at=internship.updated_at,
                                       is_open=internship.is_open)
    db.add(db_internship)
    db.commit()
    db.refresh(db_internship)
    return db_internship


def get_internship_by_name(db: Session, internship: str):
    return db.query(schemas.Internship).filter(schemas.Internship.name == internship).first()


def get_internships_by_time(db: Session, skip=0, limit=100):
    return db.query(schemas.Internship).order_by(desc(schemas.Internship.updated_at)).offset(skip).limit(limit)


def get_user_by_id(db: Session, user_id: int):
    return db.query(schemas.User).filter(schemas.User.id == user_id).first()


def get_user_by_username(db: Session, name: str):
    return db.query(schemas.User).filter(schemas.User.name == name).first()


def get_internships_by_availability(db: Session, internship_open: bool):
    return db.query(schemas.Internship).filter(schemas.Internship.is_open == internship_open).all()


def get_internship_by_id(db: Session, internship_id: int):
    return db.query(schemas.Internship).filter(schemas.Internship.id == internship_id).first()


def get_applications(db: Session, user: models.User):
    applications = db.query(schemas.Application, schemas.User, schemas.Internship).join(schemas.User).join(
        schemas.Internship).filter(schemas.User.name == user.name).all()
    result = [{'application': element[0], 'user': element[1], 'internship': element[2]} for element in applications]
    return result


def get_statistic(db: Session, id: int):
    count = db.query(schemas.Application).join(schemas.Internship).filter(schemas.Internship.id == id).count()
    applications = db.query(schemas.Application, schemas.Internship, schemas.User).join(schemas.Internship).join(
        schemas.User).filter(schemas.Internship.id == id).all()
    applications = [
        models.Application(username=application[2].name, internship=application[1].name, status=application[0].status,
                           updated_at=application[0].updated_at) for application in
        applications]
    return {'count': count, 'applications': applications}
