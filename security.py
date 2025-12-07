from cryptography.fernet import Fernet
import hashlib
import os
import jwt  
import datetime 

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