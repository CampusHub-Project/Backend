from src.models import Users, UserRole
from src.security import hash_password, verify_password, create_access_token
from tortoise.exceptions import DoesNotExist

class AuthService:
    
    @staticmethod
    async def register_user(data):
        try:
            # Okul Numarası Zorunlu
            student_number = data.get("student_number")
            if not student_number:
                return {"error": "Student number (School ID) is required"}, 400
            
            # Mükerrer Kayıt Kontrolü (ID ve Email)
            if await Users.filter(user_id=student_number).exists():
                return {"error": "Student number already registered"}, 400
            
            if await Users.filter(email=data.get("email")).exists():
                return {"error": "Email already exists"}, 400
            
            hashed = hash_password(data.get("password"))
            
            # İsim Soyisim Ayırma
            full_name = data.get("full_name", "").strip().split(" ")
            first_name = data.get("first_name", full_name[0] if full_name else "")
            last_name = data.get("last_name", " ".join(full_name[1:]) if len(full_name) > 1 else "")

            user = await Users.create(
                user_id=student_number, # Manuel ID
                email=data.get("email"),
                password=hashed,
                first_name=first_name,
                last_name=last_name,
                role=data.get("role", UserRole.STUDENT),
                department=data.get("department")
            )
            
            token = create_access_token(user.user_id, user.role.value)
            
            return {
                "token": token, 
                "user": {
                    "id": user.user_id, 
                    "email": user.email, 
                    "role": user.role.value,
                    "full_name": f"{user.first_name} {user.last_name}"
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
            user = await Users.get(email=email)
        except DoesNotExist:
            return {"error": "Invalid credentials"}, 401
            
        if not verify_password(password, user.password):
            return {"error": "Invalid credentials"}, 401
            
        token = create_access_token(user.user_id, user.role.value)
        
        return {
            "token": token, 
            "user": {
                "id": user.user_id, 
                "email": user.email, 
                "role": user.role.value,
                "full_name": f"{user.first_name} {user.last_name}"
            }
        }, 200