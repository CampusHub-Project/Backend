from functools import wraps
from sanic.response import json
from src.security import decode_access_token

def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # Header'dan token al
            token = request.token # Sanic otomatik "Authorization: Bearer <token>" kısmını ayrıştırır
            
            if not token:
                return json({"error": "Missing token"}, 401)
            
            payload = decode_access_token(token)
            
            if not payload:
                return json({"error": "Invalid or expired token"}, 401)
            
            # Kullanıcı bilgisini request objesine ekle (diğer fonksiyonlarda kullanmak için)
            request.ctx.user = payload
            
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator