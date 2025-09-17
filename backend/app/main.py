import logging
from fastapi import FastAPI, Depends
from sqlalchemy import text

from sqlalchemy.orm import Session
from . import models, db

# --- configure logging once, at startup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

@app.get("/health")
def health_check():
    try:
        # Wrap raw SQL string with text()
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        logger.error("Database connection failed", exc_info=e)
        return {"status": "error", "db": "disconnected", "detail": str(e)}