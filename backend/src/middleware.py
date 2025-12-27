from functools import wraps
from sanic.response import json
from src.security import decode_access_token
from src.models import UserRole
from src.config import logger

def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            token = request.token 
            
            if not token:
                logger.warning(f"Unauthorized access attempt to {request.path}: Missing token")
                return json({"error": "Missing token"}, 401)
            
            payload = decode_access_token(token)
            
            if not payload:
                logger.warning(f"Unauthorized access attempt to {request.path}: Invalid/Expired token")
                return json({"error": "Invalid or expired token"}, 401)
            
            if "sub" in payload and isinstance(payload["sub"], str) and payload["sub"].isdigit():
                payload["sub"] = int(payload["sub"])
            
            request.ctx.user = payload
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator

def admin_only():
    """
    Sadece 'authorized' ile birlikte kullanılır.
    Kullanıcının rolünün 'admin' olup olmadığını kontrol eder.
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if not hasattr(request.ctx, "user"):
                return json({"error": "Auth required first"}, 401)
            
            if request.ctx.user.get("role") != UserRole.ADMIN:
                logger.warning(f"Forbidden Access: User {request.ctx.user.get('sub')} tried to access Admin area.")
                return json({"error": "Admin privileges required"}, 403)
                
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator