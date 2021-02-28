import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

import sepal.db as db


class Activity(db.BaseModel, db.IdMixin):
    # TODO: once we get account creation callbacks from firebase working and can
    # guarantee every user has a profile then we should make this a proper
    # foreign key
    user_id = Column(String, nullable=False)
    # user_id = Column(String, ForeignKey("profile.user_id"), nullable=False)

    data_before = Column(pg.JSONB)
    data_after = Column(pg.JSONB)
    timestamp = Column(DateTime, server_default=db.utcnow(), nullable=False)
    table = Column(String, nullable=False)
    table_id = Column(Integer, nullable=False)

    profile = relationship(
        "Profile", primaryjoin="foreign(Activity.user_id) == remote(Profile.user_id)"
    )
