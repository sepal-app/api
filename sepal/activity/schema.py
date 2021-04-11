from datetime import datetime

from pydantic import BaseModel, root_validator


class ActivitySchemaBase(BaseModel):
    description: str


def format_user_name(profile):
    if (
        profile.family_name is not None
        and profile.family_name != ""
        and profile.given_name is not None
        and profile.given_name != ""
    ):
        return " ".join([profile.family_name, profile.given_name])
    elif profile.email is not None:
        return profile.email
    else:
        return "Unknown user"


def format_timestamp(timestamp: datetime):
    return timestamp.strftime("%b %d, %Y at %X")


def format_resource(value):
    # TODO: can we load the resource dynamically when we get the activity and
    # just call str() on it to format it
    table = value["table"]
    table_id = value["table_id"]

    if table == "taxon":
        return f"Taxon({table_id})"
    if table == "accession":
        data = (
            value["data_before"]
            if value["data_before"] is not None
            else value["data_after"]
        )
        accession_code = data["code"] if data is not None else ""
        return f"Accession {accession_code}"
    else:
        return "Unknown resource"


def description_factory(value):
    profile = value["profile"]
    user_name = format_user_name(profile) if profile is not None else "Unknown user"
    resource = format_resource(value)
    timestamp = format_timestamp(value["timestamp"])
    if value["data_after"] is None:
        return f"{resource} deleted by {user_name} on {timestamp}..."
    else:
        return f"{resource} updated by {user_name} on {timestamp}..."


class ActivitySchema(ActivitySchemaBase):
    description = ""
    timestamp = ""

    # TODO: Can we pass a link to the resource so that we can click on the item?
    # What if we want to have more than one link? Is it safe to just return
    # markup and display that?
    #
    # resource_link: str

    @root_validator(pre=True)
    def transform(cls, values):
        return {
            "description": description_factory(values),
            "timestamp": values["timestamp"].isoformat(),
        }

    class Config:
        orm_mode = True
