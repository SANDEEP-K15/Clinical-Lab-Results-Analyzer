from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE any app imports so Groq API key is available at startup
load_dotenv(Path(__file__).parent / ".env")

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    if groq_key:
        logger.info("Groq configured — model: %s", groq_model)
    else:
        logger.warning("GROQ_API_KEY not set — AI explanations will use fallback text")
    logger.info("Clinical Lab AI Analyzer backend starting")
    yield
    logger.info("Clinical Lab AI Analyzer backend shutting down")


app = FastAPI(
    title="Clinical Lab AI Analyzer",
    description="Explainable AI Laboratory Result Classification System",
    version="1.0.0",
    lifespan=lifespan,
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
