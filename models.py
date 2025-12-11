from tortoise import fields, models

# --- Ortak Miras Sınıfı (Soft Delete & Zaman Damgası) ---
class BaseModel(models.Model):
    # Her tabloda olacak ortak alanlar
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_deleted = fields.BooleanField(default=False)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True # Bu sınıf tablo olmayacak, diğerleri buradan özellik alacak

# --- Tablolar ---

class Users(BaseModel):
    # generated=False yaptık çünkü öğrenci numarasını biz gireceğiz
    user_id = fields.BigIntField(pk=True, generated=False) 
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=150, unique=True)
    password = fields.CharField(max_length=255)
    department = fields.CharField(max_length=100)
    gender = fields.CharField(max_length=10) # Enum yerine string, daha basit
    role = fields.CharField(max_length=20, default="user") # admin, user, club_admin
    profile_image = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"

class Clubs(BaseModel):
    club_id = fields.IntField(pk=True)
    club_name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(null=True)
    logo_url = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20, default="pending") # pending, active, closed
    
    # İlişkiler (Foreign Keys)
    # Tortoise'da string olarak 'models.Users' vermek circular import hatasını önler
    president = fields.ForeignKeyField('models.Users', related_name='led_clubs', on_delete=fields.SET_NULL, null=True)
    created_by = fields.ForeignKeyField('models.Users', related_name='created_clubs', on_delete=fields.SET_NULL, null=True)

    class Meta:
        table = "clubs"