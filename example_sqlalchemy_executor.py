from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from sqlalchemy import create_engine, event
from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship("Child")


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))


dburl = 'sqlite:///sa.db'
engine = create_engine(dburl)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


@contextmanager
def create_session(engine):
    session = Session(engine)
    
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


with create_session(engine) as session:
    session.add_all([
        Parent(children=[Child() for j in range(100)])
        for i in range(100)
    ])


def get_all_parents():
    with create_session(engine) as session:
        parents = session.query(Parent).all()

    return parents


with ThreadPoolExecutor(max_workers=4) as executor:
    futures_map = {executor.submit(get_all_parents): i for i in range(10000)}
    futures = as_completed(futures_map)
