from aiogram import Router

from handlers import admin, callbacks, language, start, user


def setup_routers() -> Router:
    root = Router()
    root.include_router(language.router)   # language selection must be first
    root.include_router(start.router)
    root.include_router(user.router)
    root.include_router(admin.router)
    root.include_router(callbacks.router)
    return root
