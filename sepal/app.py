import json

import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

firebase_credential = None
if settings.google_application_credentials_json is not None:
    credential_data = json.loads(settings.google_application_credentials_json)
    firebase_credential = credentials.Certificate(credential_data)

firebase_admin.initialize_app(
    credential=firebase_credential, options={"projectId": settings.firebase_project_id},
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
