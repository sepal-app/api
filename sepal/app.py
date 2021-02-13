import json
import types

import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event

import sepal.requestvars as requestvars
import sepal.db as db
from .activity.lib import track_session_listener
from .accessions.views import router as accessions_router
from .invitations.views import router as invitations_router
from .locations.views import router as locations_router
from .organizations.views import router as orgs_router
from .profile.views import router as profile_router
from .taxa.views import router as taxa_router
from .settings import settings

origins = [
    "http://localhost:3000",
    "http://sepal.app",
]

app = FastAPI()


@app.middleware("http")
async def session_tracking(request: Request, call_next):
    """Add tracking for the session.

    This is added per request so that the tracking only happens within the
    context of a request since we always want to track the user that make the
    change as well.

    """
    event.listen(db._Session, "before_flush", track_session_listener)
    response = await call_next(request)
    event.remove(db._Session, "before_flush", track_session_listener)
    return response


@app.middleware("http")
async def init_requestvars(request: Request, call_next):
    initial = types.SimpleNamespace()
    requestvars.init(initial)
    return await call_next(request)


firebase_credential = None
if settings.google_application_credentials_json is not None:
    credential_data = json.loads(settings.google_application_credentials_json)
    firebase_credential = credentials.Certificate(credential_data)

firebase_admin.initialize_app(
    credential=firebase_credential,
    options={"projectId": settings.firebase_project_id},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["link"],
)

app.include_router(accessions_router, prefix="/v1/orgs/{org_id}/accessions")
app.include_router(locations_router, prefix="/v1/orgs/{org_id}/locations")
app.include_router(orgs_router, prefix="/v1/orgs")
app.include_router(taxa_router, prefix="/v1/orgs/{org_id}/taxa")
app.include_router(profile_router, prefix="/v1/profile")
app.include_router(invitations_router, prefix="/v1/invitations")
