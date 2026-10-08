from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.exceptions.payment import (
    PaymentAlreadyExistsError,
    PaymentAppError,
    PaymentIdempotencyConflictError,
    PaymentNotFoundError,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(PaymentAlreadyExistsError)
    async def payment_already_exists_handler(
        request: Request, exc: PaymentAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "Conflict", "message": exc.message},
        )

    @app.exception_handler(PaymentIdempotencyConflictError)
    async def payment_idempotency_conflict_handler(
        request: Request, exc: PaymentIdempotencyConflictError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "Conflict", "message": exc.message},
        )

    @app.exception_handler(PaymentNotFoundError)
    async def payment_not_found_handler(request: Request, exc: PaymentNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Not Found", "message": exc.message},
        )

    @app.exception_handler(PaymentAppError)
    async def payment_base_handler(request: Request, exc: PaymentAppError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Payment Error", "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Server Error", "message": "Internal server error"},
        )
