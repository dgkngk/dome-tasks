from fastapi import APIRouter
from app.api.endpoints import auth, users#, workspaces, todolists, todos 

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(users.router, prefix="/users", tags=["users"])
# router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
# router.include_router(todolists.router, prefix="/lists", tags=["todolists"])
# router.include_router(todos.router, prefix="/todos", tags=["todos"])