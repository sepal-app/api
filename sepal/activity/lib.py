from sqlalchemy.orm import attributes
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm.exc import UnmappedColumnError
from sqlalchemy.orm.properties import RelationshipProperty
import sqlalchemy.dialects.postgresql as pg

# from sepal.db import
from sepal.requestvars import request_global
from .models import Activity


# def query_activities(mapper, id):
#     local_table = mapper.local_table.name
#     activities = session.query(Activity).filter_by(table=local_table, table_id=id).all()
#     pass


def versioned_objects(iter_):
    for obj in iter_:
        if hasattr(obj, "__track_activity__"):
            yield obj


def create_activity(obj, session, deleted=False):
    if obj.id is None:
        return
    mapper = object_mapper(obj)
    # activity_mapper = obj.__activity_mapper__
    # print(activity_mapper)
    # state = attributes.instance_state(obj)
    before = {}
    after = {}
    # attr = {}
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
    activity.data_before = before
    activity.data_after = after if not deleted else None
    activity.table = mapper.local_table.name
    activity.table_id = obj.id
    session.add(activity)
    return activity


def track_session_listener(session, _flush_context, _instances):
    for obj in versioned_objects(session.new):
        create_activity(obj, session)
    for obj in versioned_objects(session.dirty):
        create_activity(obj, session)
    for obj in versioned_objects(session.deleted):
        create_activity(obj, session, deleted=True)
