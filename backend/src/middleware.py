from functools import wraps
from sanic.response import json
from src.security import decode_access_token
from src.config import logger  # <--- Logger'ı dahil ettik

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
            # Başarılı isteklerde detay seviyesini artırmak istersen burayı açabilirsin:
            # logger.info(f"User {payload['sub']} accessing {request.path}")
            
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator