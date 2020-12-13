from sepal.db import Session
from sepal.organizations.lib import assign_role
from sepal.organizations.models import RoleType

from .models import Invitation


async def accept_invitation(token: str, user_id: str):
    with Session() as session:
        invitation = session.query(Invitation).filter_by(token=token).first()
        # TODO: make sure the invitation hasn't expired
        # TODO: make sure the invitation hasn't already been accepted
        await assign_role(invitation.organization_id, user_id, RoleType.Guest)
        return True
