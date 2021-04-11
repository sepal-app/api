import sepal.db as db

import sepal.models  # noqa: F401

from .factories import Session


def pytest_configure():
    db.metadata.create_all(bind=db.engine)


def pytest_unconfigure():
    Session.close_all()
    db.metadata.drop_all(bind=db.engine)
