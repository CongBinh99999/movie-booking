from uuid import UUID
from app.shared.exceptions import NotFoundError, ConflictError, BadRequestError


class SeatNotFoundError(NotFoundError):
    """Không tìm thấy ghế."""

    error_code = "SEAT_NOT_FOUND"

    def __init__(self, seat_id: UUID | None = None) -> None:
        self.seat_id = seat_id

        super().__init__(
            message="Không tìm thấy ghế",
            details={"seat_id": str(seat_id)} if seat_id else None
        )


class SeatAlreadyExistsError(ConflictError):
    """Ghế đã tồn tại trong phòng."""

    error_code = "SEAT_ALREADY_EXISTS"

    def __init__(self, room_id: UUID, row_label: str, seat_number: int) -> None:
        self.room_id = room_id
        self.row_label = row_label
        self.seat_number = seat_number

        super().__init__(
            message=f"Ghế {row_label}{seat_number} đã tồn tại trong phòng",
            details={
                "room_id": str(room_id),
                "row_label": row_label,
                "seat_number": seat_number
            }
        )


class SeatInactiveError(BadRequestError):
    """Ghế không hoạt động."""

    error_code = "SEAT_INACTIVE"

    def __init__(self, seat_id: UUID) -> None:
        self.seat_id = seat_id

        super().__init__(
            message="Ghế không hoạt động",
            details={"seat_id": str(seat_id)}
        )
