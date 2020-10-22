from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import db

from .accessions.views import router as accessions_router
from .locations.views import router as locations_router
from .organizations.views import router as orgs_router
from .taxa.views import router as taxa_router

origins = [
    "http://localhost:3000",
    "http://sepal.app",
]

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


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
