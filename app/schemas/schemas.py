from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Text

from app.logic.database import Base


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    updated_at = Column(DateTime(timezone=True), default=now())
    is_open = Column(Boolean, default=True)
    applications = relationship("Application")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean)
    applications = relationship("Application")


class Application(Base):
    __tablename__ = "application"

    user_id = Column(Integer, ForeignKey(User.id))
    internship_id = Column(Integer, ForeignKey(Internship.id))
    status = Column(String)
    updated_at = Column(DateTime(timezone=True), default=now())
    PrimaryKeyConstraint(user_id, internship_id)
