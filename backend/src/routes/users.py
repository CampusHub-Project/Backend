from sanic import Blueprint
from sanic.response import json
from src.services.user_service import UserService
from src.middleware import authorized

users_bp = Blueprint("users", url_prefix="/users")

@users_bp.get("/history")
@authorized()
async def get_history(request):
    user_id = request.ctx.user["sub"]
    result, status = await UserService.get_user_history(user_id)
    return json(result, status=status)

@users_bp.get("/profile")
@authorized()
async def get_profile(request):
    """Get complete user profile with all activities"""
    user_id = request.ctx.user["sub"]
    result, status = await UserService.get_user_profile(user_id)
    return json(result, status=status)

@users_bp.put("/profile")
@authorized()
async def update_profile(request):
    """Update user profile"""
    user_id = request.ctx.user["sub"]
    result, status = await UserService.update_profile(user_id, request.json)
    return json(result, status=status)