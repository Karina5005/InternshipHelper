from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.schemas import schemas
from app.controllers.routers import get_db
from app.logic.database import Base
from app.main import app
from app.models import models
from app.logic import utils

NOW = '2021-09-26T16:29:06.811823'

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    data_base = TestingSessionLocal()
    try:
        yield data_base
    finally:
        data_base.close()


def clean_db():
    data_base = TestingSessionLocal()
    try:
        data_base.query(schemas.User).delete()
        data_base.commit()
        data_base.query(schemas.Internship).delete()
        data_base.commit()
    finally:
        data_base.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_internship():
    internship = models.Internship(name="first", description="test 1", updated_at=NOW, application_num=0, is_open=True)
    assert internship.name == "first"
    assert internship.description == "test 1"
    assert internship.application_num == 0
    assert internship.is_open


def test_create_user():
    user = models.User(name="first", sex="male", status="active")
    assert user.name == "first"


def test_create_internship_db():
    clean_db()
    internship = models.Internship(name="first", description="test 1", updated_at=NOW, application_num=0, is_open=True)
    res_internship = utils.create_internship(db=TestingSessionLocal(), internship=internship)
    assert res_internship.id == 1
    assert res_internship.name == "first"
    assert res_internship.description == "test 1"
    assert res_internship.application_num == 0
    assert res_internship.is_open


def test_get_internship_by_name():
    internship = utils.get_internship_by_name(db=TestingSessionLocal(), name="first")
    assert internship.id == 1
    assert internship.name == "first"
    assert internship.description == "test 1"
    assert internship.application_num == 0
    assert internship.is_open


def test_get_internship_by_id():
    internship = utils.get_internship(db=TestingSessionLocal(), internship_id=1)
    assert internship.id == 1
    assert internship.name == "first"
    assert internship.description == "test 1"
    assert internship.application_num == 0
    assert internship.is_open


def test_create_user_db():
    clean_db()
    user = models.User(name="first", sex="male", status="active")
    res_user = utils.create_user(db=TestingSessionLocal(), user=user)
    assert res_user.id == 1
    assert res_user.name == "first"


def test_get_user_by_name():
    user = utils.get_user_by_name(db=TestingSessionLocal(), name="first")
    assert user.id == 1
    assert user.name == "first"


def test_get_user_by_id():
    user = utils.get_user(db=TestingSessionLocal(), user_id=1)
    assert user.id == 1
    assert user.name == "first"


def test_get_internship_by_open():
    clean_db()
    internship = models.Internship(name="first", description="test 1", updated_at=NOW, application_num=0, is_open=True)
    utils.create_internship(db=TestingSessionLocal(), internship=internship)
    internship = utils.get_internship_by_availability(db=TestingSessionLocal(), internship_open=True)
    assert internship.id == 1
    assert internship.name == "first"
    assert internship.description == "test 1"
    assert internship.application_num == 0
    assert internship.is_open


def test_get_internship_by_close():
    clean_db()
    internship = models.Internship(name="first", description="test 1", updated_at=NOW, application_num=0, is_open=False)
    utils.create_internship(db=TestingSessionLocal(), internship=internship)
    internship = utils.get_internship_by_availability(db=TestingSessionLocal(), internship_open=False)
    assert internship.id == 1
    assert internship.name == "first"
    assert internship.description == "test 1"
    assert internship.application_num == 0
    assert not internship.is_open


def test_get_user_by_sex_male():
    clean_db()
    user = models.User(name="first", sex="male", status="active")
    utils.create_user(db=TestingSessionLocal(), user=user)
    user = utils.get_users_by_sex(db=TestingSessionLocal(), user_sex="male")[0]
    assert user.id == 1
    assert user.name == "first"
    assert user.sex == "male"


def test_get_user_by_sex_female():
    clean_db()
    user = models.User(name="first", sex="female", status="active")
    utils.create_user(db=TestingSessionLocal(), user=user)
    user = utils.get_users_by_sex(db=TestingSessionLocal(), user_sex="female")[0]
    assert user.id == 1
    assert user.name == "first"
    assert user.sex == "female"


def test_get_user_by_sex_not_stated():
    clean_db()
    user = models.User(name="first", sex="not stated", status="active")
    utils.create_user(db=TestingSessionLocal(), user=user)
    user = utils.get_users_by_sex(db=TestingSessionLocal(), user_sex="not stated")[0]
    assert user.id == 1
    assert user.name == "first"
    assert user.sex == "not stated"


def test_get_user_by_status_active():
    clean_db()
    user = models.User(name="first", sex="female", status="active")
    utils.create_user(db=TestingSessionLocal(), user=user)
    user = utils.get_users_by_status(db=TestingSessionLocal(), user_status="active")[0]
    assert user.id == 1
    assert user.name == "first"
    assert user.sex == "female"
    assert user.status == "active"


def test_get_user_by_status_not_active():
    clean_db()
    user = models.User(name="first", sex="female", status="not active")
    utils.create_user(db=TestingSessionLocal(), user=user)
    user = utils.get_users_by_status(db=TestingSessionLocal(), user_status="not active")[0]
    assert user.id == 1
    assert user.name == "first"
    assert user.sex == "female"
    assert user.status == "not active"


def test_sign_up():
    clean_db()
    request_data = {
        "email": "vader@deathstar.com",
        "name": "Darth Vader",
        "password": "rainbow"
    }
    with TestClient(app) as t_client:
        response = t_client.post("/sign-up", json=request_data)
    assert response.status_code == 200
    print(response.json())
    assert response.json()["id"] == 1
    assert response.json()["email"] == "vader@deathstar.com"
    assert response.json()["name"] == "Darth"
    assert response.json()["token"]["expires"] is not None
    assert response.json()["token"]["access_token"] is not None
