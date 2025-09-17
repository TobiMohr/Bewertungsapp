import logging
from fastapi import FastAPI

from . import models, db
from .routers import users

# --- configure logging once, at startup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

# Create tables (only do once or at startup)
models.Base.metadata.create_all(bind=db.engine)

# Include user router
app.include_router(users.router)

