from cryptography.fernet import Fernet
import hashlib
import os

def hash_password(password: str) -> str:
    salt = os.getenv("MYSQL_ROOT_PASSWORD", "gizli_tuz") 
    salted_password = password + salt
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed

def check_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password