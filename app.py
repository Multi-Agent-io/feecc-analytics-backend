import os

from aioprometheus.asgi.middleware import MetricsMiddleware
from aioprometheus.asgi.starlette import metrics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from modules.routers import (
    employees_router,
    passports_router,
    schemas_router,
    service_router,
    stages_router,
    tcd_router,
    users_router,
)

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE", "PUT"],
    allow_headers=["*"],
)

api.add_middleware(MetricsMiddleware)
api.add_route("/metrics", metrics)

# if os.getenv("USE_HTTPS", False):
#     logger.success("Force HTTPS over HTTP enabled")
#     api.add_middleware(HTTPSRedirectMiddleware)


@api.on_event("startup")
def check_environment_variables() -> None:
    logger.info("Checking environment variables")
    failed: bool = False
    if os.environ.get("MONGO_CONNECTION_URL", None) is None:
        failed = True
        logger.error("variable $MONGO_CONNECTION_URL is not set")
    if os.environ.get("SECRET_KEY", None) is None:
        failed = True
        logger.error("variable $SECRET_KEY is not set")
    if failed:
        message = "Can't start analytics server because some envvars are missing"
        logger.critical(message)
        raise OSError(message)
    else:
        logger.info("All checks passed, running analytics server")


@api.on_event("shutdown")
def shutdown_event() -> None:
    logger.success("Shutting down feecc analytics backend server...")


api.include_router(passports_router, prefix="/api/v1/passports", tags=["Passports (Units) Management"])
api.include_router(tcd_router, prefix="/api/v1/tcd", tags=["Quality Control Operations endpoints"])
api.include_router(employees_router, prefix="/api/v1/employees", tags=["Employees Management"])
api.include_router(schemas_router, prefix="/api/v1/schemas", tags=["Production Schemas Management"])
api.include_router(stages_router, prefix="/api/v1/stages", tags=["Production Stages Management"])
api.include_router(users_router, prefix="/api/v1/users", tags=["Analytics Users Management"])
api.include_router(service_router, tags=["Service Endpoints"])
