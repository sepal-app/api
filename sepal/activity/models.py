import sepal.db as db

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, DateTime, Integer, String


class Activity(db.BaseModel, db.IdMixin):
    user_id = Column(String, nullable=False)

    data_before = Column(pg.JSONB)
    data_after = Column(pg.JSONB)
    timestamp = Column(DateTime, server_default=db.utcnow(), nullable=False)
    table = Column(String, nullable=False)
    table_id = Column(Integer, nullable=False)
