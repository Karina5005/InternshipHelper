from datetime import timedelta
from fastapi import APIRouter, status, Form
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from app.logic.database import get_db
from app.logic.utils import get_current_user
from app.models import models
from app.logic import utils_security, database

router = APIRouter()
database.Base.metadata.create_all(bind=database.engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = utils_security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils_security.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/")
async def register(username: str = Form('registration'), email: str = Form('registration'),
                   password: str = Form('registration'), db: Session = Depends(get_db)):
    user = models.UserCreate(
        name=username, email=email, password=password
    )
    try:
        user = utils_security.create_user(user=user, db=db)
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid user")


@router.get("/users/me/", response_model=models.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(current_user: models.User = Depends(get_current_user)):
    return [{"item_id": "Foo", "owner": current_user.email}]
