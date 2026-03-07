from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from uuid import UUID

from app.modules.auth.dependencies import CurrentUser
from app.modules.payments.service import PaymentServiceDep

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/vnpay/create", summary="Tạo giao dịch VNPay", status_code=201)
async def create_vnpay_payment(
    booking_id: UUID,
    current_user: CurrentUser,
    service: PaymentServiceDep,
    request: Request,
) -> dict:
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host
        or "127.0.0.1"
    )
    payment_url = await service.create_vnpay_payment(
        booking_id=booking_id,
        user_id=current_user.id,
        client_ip=client_ip,
    )
    return {"payment_url": payment_url}


@router.get("/vnpay/ipn", summary="VNPay IPN Webhook")
async def vnpay_ipn(
    request: Request,
    service: PaymentServiceDep,
) -> JSONResponse:
    """Nhận IPN từ VNPay server. Luôn trả HTTP 200, lỗi truyền qua RspCode."""
    result = await service.process_vnpay_ipn(dict(request.query_params))
    return JSONResponse(status_code=200, content=result)


@router.get("/vnpay/verify-return", summary="Verify VNPay Return URL")
async def vnpay_verify_return(
    request: Request,
    service: PaymentServiceDep,
) -> dict:
    """Verify chữ ký sau khi VNPay redirect. Chỉ dùng để render UI."""
    return await service.verify_vnpay_return(dict(request.query_params))
