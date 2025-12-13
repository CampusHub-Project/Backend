from sanic import Blueprint
from sanic.response import json
from src.services.auth_service import AuthService
from src.middleware import authorized

# Blueprint tanımla (URL ön eki /auth olacak)
auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.post("/register")
async def register(request):
    # AuthService'i çağır
    result, status = await AuthService.register_user(request.json)
    return json(result, status=status)

@auth_bp.post("/login")
async def login(request):
    result, status = await AuthService.login_user(request.json)
    return json(result, status=status)

@auth_bp.get("/me")
@authorized() # Bu endpoint korumalıdır
async def get_me(request):
    # Middleware sayesinde request.ctx.user dolu geliyor
    return json({"user": request.ctx.user})