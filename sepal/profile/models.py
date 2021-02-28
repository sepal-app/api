from sqlalchemy import Column, String

from sepal.db import Model


class Profile(Model):
    # TODO: Add an org id so user can have a separate profile per
    # organization...This might not work too well unless we have separate login
    # screens per organization. Maybe a user should enter their username and
    # password and before showing the main screen they have to select an
    # organiation instead of having the dropdown in the title bar. Then we could
    # add a menu item to switch organizations if the user has more than one.
    # This would help make the toolbar less crowded. We could also havea
    # checkbox that says, "always use this organization" so they don't have to
    # select the organiation on every login.
    #
    # org_id
    user_id = Column(String, unique=True)
    email = Column(String)
    phone_number = Column(String, default="")
    picture = Column(String, default="")

    # TODO: do we need both name and given/family name
    name = Column(String, default="")
    given_name = Column(String, default="")
    family_name = Column(String, default="")
