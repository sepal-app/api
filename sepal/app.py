from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import db

from .organizations.views import router as orgs_router
from .taxa.views import router as taxa_router
from .accessions.views import router as accessions_router

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
)
app.include_router(orgs_router, prefix="/v1/orgs")
app.include_router(taxa_router, prefix="/v1/orgs/{org_id}/taxa")
app.include_router(accessions_router, prefix="/v1/orgs/{org_id}/accessions")
