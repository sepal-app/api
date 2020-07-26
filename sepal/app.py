from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import db

from .organization.views import router as orgs_router

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
app.include_router(orgs_router, prefix="/orgs")
