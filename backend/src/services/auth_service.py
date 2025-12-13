from src.models import Users, UserRole
from src.security import hash_password, verify_password, create_access_token
from tortoise.exceptions import DoesNotExist

class AuthService:
    
    @staticmethod
    async def register_user(data):
        try:
            # E-posta kontrolü
            if await Users.filter(email=data.get("email")).exists():
                return {"error": "Email already exists"}, 400
            
            # Parolayı şifrele
            hashed = hash_password(data.get("password"))
            
            # Kullanıcıyı oluştur
            user = await Users.create(
                email=data.get("email"),
                password_hash=hashed,
                full_name=data.get("full_name"),
                role=data.get("role", UserRole.STUDENT)
            )
            
            # Token üretip döndür
            token = create_access_token(user.id, user.role.value)  # .value added for enum
            
            return {
                "token": token, 
                "user": {
                    "id": user.id, 
                    "email": user.email, 
                    "role": user.role.value,  # .value added for enum
                    "full_name": user.full_name
                }
            }, 201
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return {"error": f"Registration failed: {str(e)}"}, 500

    @staticmethod
    async def login_user(data):
        email = data.get("email")
        password = data.get("password")
        
        try:
            # Kullanıcıyı bul
            user = await Users.get(email=email)
        except DoesNotExist:
            return {"error": "Invalid credentials"}, 401
        except Exception as e:
            print(f"Login error during user fetch: {str(e)}")
            return {"error": "Login failed"}, 500
            
        # Parola doğru mu?
        if not verify_password(password, user.password_hash):
            return {"error": "Invalid credentials"}, 401
            
        # Giriş başarılı, token üret
        token = create_access_token(user.id, user.role.value)  # .value added for enum
        
        return {
            "token": token, 
            "user": {
                "id": user.id, 
                "email": user.email, 
                "role": user.role.value,  # .value added for enum
                "full_name": user.full_name
            }
        }, 200