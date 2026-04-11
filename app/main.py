from datetime import datetime
import logging
from pathlib import Path
import tomllib

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.dependencies.client_ip_provider import get_client_ip
from app.dependencies.limiter import limiter, rate_limit_exceeded_handler
from app.schemas import HealthMessageResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
)

def _get_project_version() -> str:
    pyproject_path = Path("pyproject.toml")
    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)
    return pyproject["tool"]["poetry"]["version"]


app = FastAPI(
    title="Office Chat API",
    description="API de Serviços do Office Chat",
    version=_get_project_version(),
    docs_url="/api/core/docs",
    redoc_url="/api/core/redoc",
    openapi_url="/api/core/openapi.json",
)

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter  # type: ignore
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.get("/api/core/health", tags=["Health"], response_model=HealthMessageResponse)
async def root(request: Request, client_ip: str = Depends(get_client_ip)):
    server_ip: str = request.scope.get("server")[0]
    api_version: str = request.app.version

    return HealthMessageResponse(
        client_ip=client_ip,
        server_ip=server_ip,
        current_date_time=datetime.now(),
        api_version=api_version,
        message="Core Running OK",
    )


app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
