"""Movies router.

TODO: Implement endpoints:
- GET    /api/v1/movies           (list, paginated)
- GET    /api/v1/movies/{id}      (get one)
- POST   /api/v1/movies           (create - admin only)
- PUT    /api/v1/movies/{id}      (update - admin only)
- DELETE /api/v1/movies/{id}      (delete - admin only)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/movies", tags=["Movies"])

# TODO: Implement endpoints
