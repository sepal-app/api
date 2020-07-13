# -*- coding: utf-8 -*-
#
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .users.views import router as users_router

# from .oauth2.views import router as oauth2_router
from .organizations.views import router as orgs_router

origins = [
    "http://localhost:3000",
    "http://sepal.app",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router, prefix="/users")
app.include_router(orgs_router, prefix="/orgs")
