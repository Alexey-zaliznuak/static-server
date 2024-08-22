import os
import sys

sys.path.append(os.path.dirname(__file__))

from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from domain.files.router import router as files_router
from infrastructure.database import tortoise_shutdown, tortoise_startup
from infrastructure.openapi import build_custom_openapi_schema
from infrastructure.rate_limit import limiter
from infrastructure.route.middlewares import ProcessTimeMiddleware

app = FastAPI(docs_url="/api/docs")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_event_handler("startup", tortoise_startup)
app.add_event_handler("shutdown", tortoise_shutdown)

app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test/ping", response_model=Literal["pong"])
def ping():
    return "pong"


app.include_router(files_router)

app.openapi_schema = build_custom_openapi_schema(app)
