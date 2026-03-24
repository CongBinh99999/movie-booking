"""Payment repository - data access layer for Payment entity.

TODO: Implement PaymentRepository with methods:

# CRUD cơ bản
- get_by_id(payment_id: UUID) -> Payment | None
- get_by_transaction_id(transaction_id: str) -> Payment | None
- create(data: PaymentCreate) -> Payment
- update(payment: Payment, data: PaymentUpdate) -> Payment

# Query methods
- get_by_booking(booking_id: UUID) -> list[Payment]
- get_by_status(status: PaymentStatus, skip: int = 0, limit: int = 100) -> list[Payment]
- get_by_method(method: PaymentMethod, skip: int = 0, limit: int = 100) -> list[Payment]
- get_latest_by_booking(booking_id: UUID) -> Payment | None
  - Get most recent payment for a booking
- count_by_status(status: PaymentStatus) -> int

# Status updates
- update_status(payment_id: UUID, status: PaymentStatus) -> Payment | None
- mark_as_completed(payment_id: UUID, transaction_id: str, callback_data: dict) -> Payment | None
  - Set status=COMPLETED, paid_at=now(), transaction_id, callback_data
- mark_as_failed(payment_id: UUID, reason: str) -> Payment | None
  - Set status=FAILED, failed_at=now(), failure_reason
- mark_as_refunded(payment_id: UUID) -> Payment | None
  - Set status=REFUNDED

# Helpers
- exists_by_transaction_id(transaction_id: str) -> bool

# With relationships
- get_by_id_with_booking(payment_id: UUID) -> Payment | None
  - Eager load booking

# Admin/Reporting
- get_revenue_by_date_range(start: date, end: date) -> Decimal
  - Sum of completed payments
- get_payments_by_date_range(start: date, end: date, status: PaymentStatus | None) -> list[Payment]
"""
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func, desc, exists, and_
from sqlalchemy.orm import selectinload
from sqlmodel import col
from datetime import datetime, timezone, date
from decimal import Decimal


from app.shared.dependencies import DbSession
from app.modules.payments.models import Payments, PaymentStatus, PaymentMethod
from app.modules.payments.schemas.domain import PaymentCreate, PaymentUpdate


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, payment_id: UUID) -> Payments | None:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.id == payment_id)
        )

        return result.scalar_one_or_none()

    async def get_by_transaction_id(self, transaction_id: str) -> Payments | None:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.transaction_id == transaction_id)
        )

        return result.scalar_one_or_none()

    async def create(self, data: PaymentCreate) -> Payments:
        payment = Payments(**data.model_dump())
        self.db.add(payment)
        await self.db.flush()
        return payment

    async def update(self, payment: Payments, data: PaymentUpdate) -> Payments:
        updated_data = data.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(payment, key, value)

        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def get_by_booking(self, booking_id: UUID) -> list[Payments]:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.booking_id == booking_id)
        )

        return list(result.scalars().all())

    async def get_by_status(self, status: PaymentStatus, skip: int = 0, limit: int = 100) -> list[Payments]:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.status == status)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_method(self, method: PaymentMethod, skip: int = 0, limit: int = 100) -> list[Payments]:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.payment_method == method)
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_latest_by_booking(self, booking_id: UUID) -> Payments | None:
        result = await self.db.execute(
            select(Payments)
            .where(Payments.booking_id == booking_id)
            .order_by(desc(Payments.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def count_by_status(self, status: PaymentStatus) -> int:
        result = await self.db.execute(
            select(func.count(Payments.id))
            .select_from(Payments)
            .where(Payments.status == status)
        )

        return result.scalar_one()

    async def update_status(self, payment: Payments, status: PaymentStatus) -> Payments:
        payment.status = status
        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def mark_as_completed(self, payment: Payments, transaction_id: str, callback_data: dict) -> Payments:
        payment.transaction_id = transaction_id
        payment.callback_data = callback_data
        payment.status = PaymentStatus.COMPLETED
        payment.paid_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def mark_as_failed(self, payment: Payments, reason: str) -> Payments:
        payment.failure_reason = reason
        payment.status = PaymentStatus.FAILED
        payment.failed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def mark_as_refunded(self, payment: Payments) -> Payments:
        payment.status = PaymentStatus.REFUNDED
        await self.db.flush()
        await self.db.refresh(payment)

        return payment

    async def exists_by_transaction_id(self, transaction_id: str) -> bool:
        result = await self.db.execute(
            select(
                exists().where(
                    Payments.transaction_id == transaction_id
                )
            )
        )

        return bool(result.scalar_one())

    async def get_by_id_with_booking(self, payment_id: UUID) -> Payments | None:
        """Lấy payment kèm booking (eager load)."""
        result = await self.db.execute(
            select(Payments)
            .where(Payments.id == payment_id)
            .options(selectinload(Payments.booking))
        )
        return result.scalar_one_or_none()

    # ============ Admin/Reporting ============

    async def get_revenue_by_date_range(
        self,
        start: date,
        end: date
    ) -> Decimal:
        end_datetime = datetime.combine(end, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )
        start_datetime = datetime.combine(start, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )

        result = await self.db.execute(
            select(func.coalesce(func.sum(Payments.amount), 0))
            .select_from(Payments)
            .where(
                and_(
                    Payments.status == PaymentStatus.COMPLETED,
                    col(Payments.paid_at).isnot(None),
                    col(Payments.paid_at) >= start_datetime,
                    col(Payments.paid_at) <= end_datetime
                )
            )
        )

        return result.scalar() or Decimal("0")

    async def get_payments_by_date_range(
        self,
        start: date,
        end: date,
        status: PaymentStatus | None = None
    ) -> list[Payments]:
        end_datetime = datetime.combine(end, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )
        start_datetime = datetime.combine(start, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )

        conditions = [
            Payments.created_at >= start_datetime,
            Payments.created_at <= end_datetime
        ]

        if status is not None:
            conditions.append(Payments.status == status)

        result = await self.db.execute(
            select(Payments)
            .where(*conditions)
            .order_by(desc(Payments.created_at))
        )

        return list(result.scalars().all())


def get_payment_repository(
    db: DbSession
) -> PaymentRepository:
    return PaymentRepository(db)


PaymentRepoDeps = Annotated[PaymentRepository, Depends(get_payment_repository)]
