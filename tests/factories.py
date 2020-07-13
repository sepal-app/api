import factory
import factory.fuzzy
from sqlalchemy.orm import scoped_session, sessionmaker

import sepal.db as db
from sepal.users.models import User


# session = db.Session()
Session = scoped_session(sessionmaker(bind=db.engine))


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    username = factory.fuzzy.FuzzyText(prefix="user")
    email = factory.Faker("email")
