"""Aggregate domain routers under a single API router."""

from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.chat.router import router as chat_router
from src.config.router import router as config_router
from src.notifications.router import router as notifications_router
from src.profiles.router import router as profiles_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profiles_router)
api_router.include_router(chat_router)
api_router.include_router(notifications_router)
api_router.include_router(config_router)
