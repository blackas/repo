from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .stocks import router as stocks_router
from .crypto import router as crypto_router
from .watchlists import router as watchlists_router
from .reports import router as reports_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(stocks_router)
api_router.include_router(crypto_router)
api_router.include_router(watchlists_router)
api_router.include_router(reports_router)
