import sepal.db as db

import sepal.models  # noqa: F401


def pytest_configure():
    db.metadata.create_all(bind=db.engine)


def pytest_unconfigure():
    db.metadata.drop_all(bind=db.engine)
