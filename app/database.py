import os

from sqlalchemy import create_engine

from models import Base
from test_objects import create_default_objects


def create_db_and_tables():
    db_url = os.environ.get('DB_URL')
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    create_default_objects(engine)
    conn = engine.connect()
    return conn, Base.metadata
