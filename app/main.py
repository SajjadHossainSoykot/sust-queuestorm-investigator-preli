"""FastAPI entrypoint for the SUST preliminary QueueStorm Investigator service."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.investigator import analyze_ticket
from app.schemas import AnalyzeTicketRequest, AnalyzeTicketResponse, ErrorResponse

logger = logging.getLogger("queuestorm")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="QueueStorm Investigator",
    description="Evidence-grounded AI/API SupportOps copilot for SUST CSE Carnival 2026 preliminary round.",
    version="1.0.0",
)


@app.get("/", tags=["info"])
def root() -> dict[str, str]:
    return {
        "service": "QueueStorm Investigator",
        "health": "/health",
        "analyze_ticket": "/analyze-ticket",
    }


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/analyze-ticket",
    response_model=AnalyzeTicketResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["analysis"],
)
def analyze_ticket_endpoint(payload: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    return analyze_ticket(payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Do not expose stack traces or internal details. Keep enough context for judging/debugging.
    logger.info("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Invalid request schema or semantic input. Check required fields and enum values."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error. Please retry or check service logs."},
    )
