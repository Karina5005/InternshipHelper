import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session

from app.logic.database import get_db
from app.models import models
from app.logic import utils, database

router = APIRouter()
database.Base.metadata.create_all(bind=database.engine)


@router.get("/internships/name", response_model=models.Internship)
def get_internships(name, db: Session = Depends(get_db)):
    internship = utils.get_internship_by_name(db, internship=name)
    return models.Internship(name=internship.name, description=internship.description, updated_at=internship.updated_at,
                             is_open=internship.is_open)


@router.get("/internships/newest", response_model=List[models.Internship])
def get_internships_by_time(db: Session = Depends(get_db)):
    internships = utils.get_internships_by_time(db)
    return [models.Internship(name=internship.name, description=internship.description,
                              updated_at=internship.updated_at,
                              is_open=internship.is_open) for internship in internships]


@router.get("/internships/open", response_model=List[models.Internship])
def get_internships_by_time(db: Session = Depends(get_db)):
    internships = utils.get_internships_by_availability(db, True)
    return [models.Internship(name=internship.name, description=internship.description,
                              updated_at=internship.updated_at,
                              is_open=internship.is_open) for internship in internships]


@router.get("/internships/close", response_model=List[models.Internship])
def get_internships_by_time(db: Session = Depends(get_db)):
    internships = utils.get_internships_by_availability(db, False)
    return [models.Internship(name=internship.name, description=internship.description,
                              updated_at=internship.updated_at,
                              is_open=internship.is_open) for internship in internships]


@router.post("/internships/new", response_model=models.Internship)
def create_internships(db: Session = Depends(get_db), internship: models.Internship = None):
    if internship is None:
        raise HTTPException(status_code=400, detail="Invalid data")
    utils.create_internship(db, internship)
    return internship


@router.post("/internships/{id}/application", response_model=models.Application)
def create_application(db: Session = Depends(get_db), id: int = None, status: str = None,
                       current_user: models.User = Depends(utils.get_current_user)):
    if status is None or id is None:
        raise HTTPException(status_code=400, detail="Invalid url")
    utils.create_application(db, id, status, current_user)
    return models.Application(status=status, updated_at=datetime.datetime.now())


@router.get("/internships/{id}/statistic", response_model=models.Statistic)
def get_statistic(db: Session = Depends(get_db), id: int = None):
    if id is None:
        raise HTTPException(status_code=400, detail="Invalid url")
    stat = utils.get_statistic(db, id)
    return models.Statistic(count=stat['count'], applications=stat['applications'])


@router.post("/user/applications", response_model=List[models.Application])
def get_applications(db: Session = Depends(get_db), current_user: models.User = Depends(utils.get_current_user)):
    applications_info = utils.get_applications(db, current_user)
    return [models.Application(username=application_info['user'].name, internship=application_info['internship'].name,
                               status=application_info['application'].status,
                               updated_at=application_info['application'].updated_at) for application_info in
            applications_info]
