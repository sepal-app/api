from base64 import b64decode
from contextlib import contextmanager
from enum import Enum
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy import event, select
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import RelationshipProperty, attributes, joinedload, object_mapper
from sqlalchemy.orm.exc import UnmappedColumnError

import sepal.db as db
from sepal.profile.models import Profile
from sepal.requestvars import request_global

from .models import Activity


class ActivityPermission(str, Enum):
    Read = "activity:read"


#
async def get_activity(
    org_id: str,
    limit: int = 50,
    cursor: str = None,
    include: Optional[List[str]] = None,
) -> List[Activity]:
    with db.Session() as session:
        q = (
            select(Activity)
            .where(
                sa.or_(
                    Activity.data_before["org_id"].as_integer() == org_id,
                    Activity.data_after["org_id"].as_integer() == org_id,
                ),
            )
            .order_by(Activity.timestamp.desc())
        )
        q = q.options(joinedload(Activity.profile))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.where(Activity.timestamp > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Activity, field)))

        q = q.limit(limit)
        return session.execute(q).scalars().all()


def versioned_objects(iter_):
    for obj in iter_:
        if hasattr(obj, "__track_activity__"):
            yield obj


def create_activity(obj, session, state=None):
    """Create a new activity.

    This function will only work in the context of a request since it requires
    that the current_user_id is set in the request_global()

    """
    if obj.id is None:
        # We can't create an activity for a resource without an id. This can
        # happen if this funtion is called in the "before_flush" event for new
        # objects. When we call this in the "after_flush" the object will still
        # be in session.new but will now have an id.
        return

    mapper = object_mapper(obj)
    before = {}
    after = {}
    obj_changed = False
    for om in mapper.iterate_to_root():
        for col in om.local_table.c:
            # get the value of the
            # attribute based on the MapperProperty related to the
            # mapped column.  this will allow usage of MapperProperties
            # that have a different keyname than that of the mapped column.
            try:
                prop = mapper.get_property_by_column(col)
            except UnmappedColumnError:
                # in the case of single table inheritance, there may be
                # columns on the mapped table intended for the subclass only.
                # the "unmapped" status of the subclass column on the
                # base class is a feature of the declarative module.
                continue

            # expired object attributes and also deferred cols might not be in
            # the dict. getting the attribute will force it to load no matter
            # what
            after[prop.key] = getattr(obj, prop.key)

            added, unchanged, deleted_attrs = attributes.get_history(obj, prop.key)

            if deleted_attrs:
                obj_changed = True
                before[prop.key] = deleted_attrs[0]
            elif unchanged:
                before[prop.key] = unchanged[0]
            elif added:
                # if the attribute had no value.
                # TODO: how do we get the previous value....maybe we just get
                # the default value for the field...what what if the field
                before[prop.key] = None
                obj_changed = True

    if not obj_changed:
        # not changed, but we have relationships.  OK
        # check those too
        for prop in mapper.iterate_properties:
            if (
                isinstance(prop, RelationshipProperty)
                and attributes.get_history(
                    obj, prop.key, passive=attributes.PASSIVE_NO_INITIALIZE
                ).has_changes()
            ):
                for p in prop.local_columns:
                    if p.foreign_keys:
                        obj_changed = True
                        break
                if obj_changed is True:
                    break

    activity = Activity()
    activity.user_id = request_global().current_user_id
    activity.data_before = before if state != "new" else None
    activity.data_after = after if state != "deleted" else None
    activity.table = mapper.local_table.name
    activity.table_id = obj.id
    session.add(activity)
    return activity


def before_flush_listener(session, _flush_context, _instances=None):
    for obj in versioned_objects(session.dirty):
        create_activity(obj, session, state="dirty")
    for obj in versioned_objects(session.deleted):
        create_activity(obj, session, state="deleted")


def after_flush_listener(session, _flush_context):
    # In order to create an activity for the new objects we need the objects
    # id which doesn't get assigned until after a flush which means we need
    # to create our own session and merge the activity into it so we can
    # commit it since the original session might not get flushed again.
    new_session = db.session_factory()
    for obj in versioned_objects(session.new):
        activity = create_activity(obj, session, state="new")
        new_session.merge(activity)

    new_session.flush()


def init_session_tracking(session):
    event.listen(session, "before_flush", before_flush_listener)
    event.listen(session, "after_flush", after_flush_listener)

    def unregister():
        if event.contains(session, "before_flush", before_flush_listener):
            event.remove(session, "before_flush", before_flush_listener)
        if event.contains(session, "after_flush", after_flush_listener):
            event.remove(session, "after_flush", after_flush_listener)

    return unregister
