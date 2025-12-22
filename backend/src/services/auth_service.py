from src.models import Users, UserRole
from src.security import hash_password, verify_password, create_access_token
from tortoise.exceptions import DoesNotExist
from src.config import logger

class AuthService:
    
    @staticmethod
    async def register_user(data):
        try:
            student_number = data.get("student_number")
            email = data.get("email")

            if not student_number:
                logger.warning("Registration failed: Missing student number")
                return {"error": "Student number (School ID) is required"}, 400
            
            if await Users.filter(user_id=student_number).exists():
                logger.warning(f"Registration failed: Duplicate ID {student_number}")
                return {"error": "Student number already registered"}, 400
            
            if await Users.filter(email=email).exists():
                logger.warning(f"Registration failed: Duplicate Email {email}")
                return {"error": "Email already exists"}, 400
            
            hashed = hash_password(data.get("password"))
            
            full_name = data.get("full_name", "").strip().split(" ")
            first_name = data.get("first_name", full_name[0] if full_name else "")
            last_name = data.get("last_name", " ".join(full_name[1:]) if len(full_name) > 1 else "")

            user = await Users.create(
                user_id=student_number,
                email=email,
                password=hashed,
                first_name=first_name,
                last_name=last_name,
                role=data.get("role", UserRole.STUDENT),
                department=data.get("department")
            )
            
            token = create_access_token(user.user_id, user.role.value)
            
            logger.info(f"New User Registered: {user.email} (ID: {user.user_id})")
            
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
            logger.error(f"CRITICAL Registration Error: {str(e)}", exc_info=True)
            return {"error": f"Registration failed: {str(e)}"}, 500

    @staticmethod
    async def login_user(data):
        email = data.get("email")
        
        try:
            user = await Users.get(email=email)
        except DoesNotExist:
            logger.warning(f"Login failed: Email not found - {email}")
            return {"error": "Invalid credentials"}, 401
            
        # --- EKLENEN KISIM: Silinmiş kullanıcı kontrolü ---
        if user.is_deleted:
            logger.warning(f"Login failed: Banned/Deleted User - {email}")
            return {"error": "Account is disabled. Please contact admin."}, 403
        # --------------------------------------------------

        if not verify_password(data.get("password"), user.password):
            logger.warning(f"Login failed: Wrong password - {email}")
            return {"error": "Invalid credentials"}, 401
            
        token = create_access_token(user.user_id, user.role.value)
        logger.info(f"User Logged In: {user.email}")
        
        return {
            "token": token, 
            "user": {
                "id": user.user_id, 
                "email": user.email, 
                "role": user.role.value,
                "full_name": f"{user.first_name} {user.last_name}"
            }
        }, 200