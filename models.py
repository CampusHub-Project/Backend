from tortoise import fields, models

# --- Ortak Miras Sınıfı ---
class BaseModel(models.Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_deleted = fields.BooleanField(default=False)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

# --- 1. Kullanıcılar ---
class Users(BaseModel):
    user_id = fields.BigIntField(pk=True, generated=False) 
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=150, unique=True)
    password = fields.CharField(max_length=255)
    department = fields.CharField(max_length=100)
    gender = fields.CharField(max_length=10)
    role = fields.CharField(max_length=20, default="user")
    profile_image = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"

# --- 2. Kulüpler ---
class Clubs(BaseModel):
    club_id = fields.IntField(pk=True)
    club_name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(null=True)
    logo_url = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20, default="pending")
    
    # İlişkiler
    president = fields.ForeignKeyField('models.Users', related_name='led_clubs', on_delete=fields.SET_NULL, null=True)
    created_by = fields.ForeignKeyField('models.Users', related_name='created_clubs', on_delete=fields.SET_NULL, null=True)

    class Meta:
        table = "clubs"

# --- 3. Etkinlikler (YENİ EKLENEN KISIM) ---
class Events(BaseModel):
    event_id = fields.IntField(pk=True)
    # Hangi kulüp düzenliyor?
    club = fields.ForeignKeyField('models.Clubs', related_name='events')
    
    title = fields.CharField(max_length=150)
    description = fields.TextField(null=True)
    image_url = fields.CharField(max_length=255, null=True)
    event_date = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True)
    location = fields.CharField(max_length=255, null=True)
    quota = fields.IntField(default=0)
    
    created_by = fields.ForeignKeyField('models.Users', related_name='created_events', on_delete=fields.SET_NULL, null=True)

    class Meta:
        table = "events"

# --- 4. Etkinlik Katılımcıları (YENİ) ---
class EventParticipants(models.Model):
    participant_id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Events', related_name='participants')
    user = fields.ForeignKeyField('models.Users', related_name='participated_events')
    status = fields.CharField(max_length=20, default="going") # going, interested, not_going
    joined_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "event_participants"
        unique_together = (("event", "user"),)

# --- 5. Bildirimler (YENİ) ---
class Notifications(models.Model):
    notification_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='notifications')
    club = fields.ForeignKeyField('models.Clubs', related_name='club_notifications', null=True)
    event = fields.ForeignKeyField('models.Events', related_name='event_notifications', null=True)
    message = fields.CharField(max_length=255)
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"