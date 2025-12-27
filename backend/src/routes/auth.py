from sanic import Blueprint
from sanic.response import json
from src.services.auth_service import AuthService
from src.middleware import authorized

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.post("/register")
async def register(request):
    result, status = await AuthService.register_user(request.json)
    return json(result, status=status)

@auth_bp.post("/login")
async def login(request):
    result, status = await AuthService.login_user(request.json)
    return json(result, status=status)

@auth_bp.get("/me")
@authorized()
async def get_me(request):
    return json({"user": request.ctx.user})