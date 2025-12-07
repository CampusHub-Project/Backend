from cryptography.fernet import Fernet
import hashlib
import os
import jwt  
import datetime 
from functools import wraps
from sanic.response import json

SECRET_KEY = os.getenv("MYSQL_ROOT_PASSWORD", "cok_gizli_anahtar")

def hash_password(password: str) -> str:
    salt = os.getenv("MYSQL_ROOT_PASSWORD", "gizli_tuz") 
    salted_password = password + salt
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed

def check_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            token = request.token
            
            if not token:
                return json({"error": "Giriş yapmanız gerekiyor (Token eksik)."}, status=401)

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                
                request.ctx.user_id = payload["user_id"]
                
            except jwt.ExpiredSignatureError:
                return json({"error": "Oturum süresi dolmuş. Tekrar giriş yapın."}, status=401)
            except jwt.InvalidTokenError:
                return json({"error": "Geçersiz Token!"}, status=401)

            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator