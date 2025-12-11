from sanic import Blueprint
from sanic.response import json
from models import Users 
from security import hash_password, check_password, create_access_token, authorized
from tortoise.exceptions import IntegrityError

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.post("/register")
async def register(request):
    data = request.json
    
    required = ["user_id", "first_name", "last_name", "email", "password", "department", "gender"]
    if not all(k in data for k in required):
        return json({"error": "Eksik bilgi gönderildi."}, status=400)

    try:
        user = await Users.create(
            user_id=data["user_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=hash_password(data["password"]),
            department=data["department"],
            gender=data["gender"]
        )
        return json({"message": "Kayıt başarılı!", "user_id": user.user_id}, status=201)

    except IntegrityError:
        return json({"error": "Bu kullanıcı zaten kayıtlı (ID veya Email kullanımda)."}, status=409)
    except Exception as e:
        return json({"error": str(e)}, status=500)

@auth_bp.post("/login")
async def login(request):
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return json({"error": "Email ve şifre gereklidir."}, status=400)

    user = await Users.get_or_none(email=data["email"])

    if not user:
        return json({"error": "Kullanıcı bulunamadı."}, status=404)

    if not check_password(data["password"], user.password):
        return json({"error": "Hatalı şifre!"}, status=401)

    token = create_access_token(user.user_id)

    return json({
        "message": "Giriş başarılı!",
        "token": token,
        "user": {
            "first_name": user.first_name,
            "role": user.role
        }
    })

@auth_bp.get("/me")
@authorized()
async def get_my_profile(request):
    user_id = request.ctx.user_id
    
    user = await Users.get(user_id=user_id)
    
    return json({
        "user": {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    })