from sqlalchemy import Column, DateTime, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

db = create_engine("sqlite:///db.sqlite3", connect_args={'check_same_thread': False})
base = declarative_base()
Session = sessionmaker(bind=db)


class config(base):
    __tablename__ = 'base_config'
    key = Column(String, primary_key=True)
    value = Column(String)


class bds_log(base):
    __tablename__ = 'bds_log'
    time = Column(DateTime, primary_key=True, index=True)
    log_type = Column(String)
    log = Column(String)


def create_db():
    base.metadata.create_all(db)


def drop_db():
    base.metadata.drop_all(db)


def get_session():
    session = scoped_session(Session)
    return session
