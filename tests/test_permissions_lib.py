from random import choice

from sepal.permissions.lib import (
    assign_user_role,
    grant_role_permission,
    grant_user_permission,
    has_permission,
    is_role_member,
    remove_user_role,
    revoke_role_permission,
    revoke_user_permission,
)
from .fixtures import *  # noqa: F401,F403


def test_user_has_permission(org, current_user_id, random_permission):
    # revoke the permission first since the user is the owner of the
    # organization and already has full permissions
    revoke_user_permission(org.id, current_user_id, random_permission)
    assert has_permission(org.id, current_user_id, random_permission) is False

    grant_user_permission(org.id, current_user_id, random_permission)
    assert has_permission(org.id, current_user_id, random_permission)


def test_assign_user_role(current_user_id, role):
    assign_user_role(current_user_id, role.id)
    assert is_role_member(current_user_id, role.id)


def test_remove_user_role(current_user_id, role, make_token):
    assign_user_role(current_user_id, role.id)
    assert is_role_member(current_user_id, role.id)

    remove_user_role(current_user_id, role.id)
    assert is_role_member(current_user_id, role.id) is False


def test_users_role_has_permission(org, current_user_id, role, random_permission):
    revoke_user_permission(org.id, current_user_id, random_permission)
    assert has_permission(org.id, current_user_id, random_permission) is False

    assign_user_role(current_user_id, role.id)
    grant_role_permission(role.id, random_permission)
    assert has_permission(org.id, current_user_id, random_permission)

    revoke_role_permission(role.id, random_permission)
    assert has_permission(org.id, current_user_id, random_permission) is False
