from sanic import Blueprint
from sanic.response import json
from database import execute_query, fetch_one
from security import hash_password

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.post("/register")
async def register(request):
    data = request.json
    
    required_fields = ["user_id", "first_name", "last_name", "email", "password", "department", "gender"]
    for field in required_fields:
        if field not in data:
            return json({"error": f"Eksik bilgi: {field}"}, status=400)

    existing_user = await fetch_one(
        "SELECT user_id FROM Users WHERE email = %s OR user_id = %s", 
        (data["email"], data["user_id"])
    )
    
    if existing_user:
        return json({"error": "Bu kullanıcı zaten kayıtlı (Email veya ID kullanımda)."}, status=409)

    hashed_pw = hash_password(data["password"])

    try:
        await execute_query(
            """
            INSERT INTO Users (user_id, first_name, last_name, email, password, department, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["user_id"],
                data["first_name"],
                data["last_name"],
                data["email"],
                hashed_pw,
                data["department"],
                data["gender"]
            )
        )
        return json({"message": "Kayıt başarılı!", "user_id": data["user_id"]}, status=201)
        
    except Exception as e:
        return json({"error": str(e)}, status=500)