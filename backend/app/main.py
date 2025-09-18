import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, db
from .routers import users, auth

# --- configure logging once, at startup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app first
app = FastAPI()

# CORSMiddleware must come BEFORE routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables at startup
logger.info("Creating database tables if they don't exist…")
models.Base.metadata.create_all(bind=db.engine)

# Include user router
app.include_router(users.router)
app.include_router(auth.router)
