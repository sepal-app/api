from sqlalchemy import Column, String

from sepal.db import Model


class Profile(Model):
    user_id = Column(String, unique=True)
    email = Column(String)
    phone_number = Column(String, default="")
    picture = Column(String, default="")
    name = Column(String, default="")
    given_name = Column(String, default="")
    family_name = Column(String, default="")
