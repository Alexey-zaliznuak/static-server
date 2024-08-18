import os
import sys

sys.path.append(os.path.dirname(__file__))

from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from infrastructure.openapi import build_custom_openapi_schema
from infrastructure.rate_limit import limiter
from infrastructure.route.middlewares import ProcessTimeMiddleware


app = FastAPI(docs_url="/api/docs")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(your_model_router)

app.include_router(v1_router)


@app.get("/ping", response_model=Literal["pong"])
def ping():
    return {"message": "pong"}

app.openapi_schema = build_custom_openapi_schema(app)
