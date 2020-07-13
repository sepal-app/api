import asyncio

import sepal.db as db
import sepal.models


def pytest_configure():
    db.metadata.create_all(bind=db.engine)


def pytest_unconfigure():
    db.metadata.drop_all(bind=db.engine)
