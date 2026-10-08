from dataclasses import dataclass
from uuid import UUID


@dataclass
class PaymentAppError(Exception):
    def __post_init__(self):
        super().__init__(self.message)

    @property
    def message(self) -> str:
        return "Произошла ошибка в приложении платежей"


@dataclass
class PaymentAlreadyExistsError(PaymentAppError):
    key: str

    @property
    def message(self) -> str:
        return f"Платеж с ключом: {self.key} уже есть."


@dataclass
class PaymentIdempotencyConflictError(PaymentAppError):
    key: str

    @property
    def message(self) -> str:
        return (
            f"Idempotency-Key '{self.key}' уже использован с другим телом запроса."
        )


@dataclass
class PaymentNotFoundError(PaymentAppError):
    payment_id: UUID

    @property
    def message(self) -> str:
        return f"Платеж с ID: {self.payment_id} не найден."
