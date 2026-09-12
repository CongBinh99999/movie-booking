# Tests

```bash
pytest                                    # chỉ unit test (20)
TEST_DATABASE_URL=postgresql+asyncpg://user:pw@localhost:5432/mb_test pytest   # đủ 34
```

Không đặt `TEST_DATABASE_URL` thì test tích hợp tự skip — suite vẫn chạy được
ở mọi máy. DB test bị `TRUNCATE ... CASCADE` sau **mỗi** test, đừng trỏ vào DB
có dữ liệu thật.

Redis được thay bằng `fakeredis` ở mọi test, không cần server Redis.

| File | Loại | Nội dung |
|---|---|---|
| `test_auth_security.py` | unit | loại token, thu hồi khi xoay, gộp lỗi đăng nhập |
| `test_seat_lock_lifecycle.py` | unit | trả lock khi lỗi, bỏ qua lock của chính mình |
| `test_showtime_validation.py` | unit | trùng giờ trong bulk, dời về quá khứ, số booking |
| `test_vnpay_payment.py` | unit | chữ ký, IPN, hoàn tiền thủ công |
| `test_expire_bookings_task.py` | unit | khoá chống chạy trùng, vòng lặp chịu lỗi |
| `test_pagination_integration.py` | tích hợp | `total` là tổng thật, không phải cỡ trang |
| `test_expire_bookings_integration.py` | tích hợp | ghế được trả lại khi booking hết hạn |
| `test_api_smoke.py` | tích hợp | luồng auth qua HTTP, router gắn đúng |
