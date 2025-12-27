from tortoise import fields, models
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    CLUB_ADMIN = "club_admin"
    ADMIN = "admin"

class ParticipationStatus(str, Enum):
    GOING = "going"
    INTERESTED = "interested"

class BaseModel(models.Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_deleted = fields.BooleanField(default=False)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True


class Users(BaseModel):
    user_id = fields.BigIntField(pk=True, generated=False) 
    
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=150, unique=True, index=True)
    password = fields.CharField(max_length=255)
    
    # Profil detayları
    department = fields.CharField(max_length=100, null=True)
    gender = fields.CharField(max_length=10, null=True)
    profile_image = fields.CharField(max_length=255, null=True)
    bio = fields.TextField(null=True)
    interests = fields.TextField(null=True)
    
    role = fields.CharEnumField(UserRole, default=UserRole.STUDENT)

    class Meta:
        table = "users"

class Clubs(BaseModel):
    club_id = fields.IntField(pk=True)
    club_name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(null=True)
    logo_url = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20, default="active")
    
    # Kulüp Başkanı ve Oluşturan Kişi
    president = fields.ForeignKeyField('models.Users', related_name='led_clubs', on_delete=fields.SET_NULL, null=True)
    created_by = fields.ForeignKeyField('models.Users', related_name='created_clubs', on_delete=fields.SET_NULL, null=True)

    class Meta:
        table = "clubs"

class ClubFollowers(BaseModel):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='following')
    club = fields.ForeignKeyField('models.Clubs', related_name='followers')

    class Meta:
        table = "club_followers"
        unique_together = ("user", "club")

class Events(BaseModel):
    event_id = fields.IntField(pk=True)
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

class EventParticipation(BaseModel):
    participation_id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Events', related_name='participants')
    user = fields.ForeignKeyField('models.Users', related_name='participated_events')
    status = fields.CharEnumField(ParticipationStatus, default=ParticipationStatus.GOING)
    
    class Meta:
        table = "event_participants"
        unique_together = ("event", "user")

class EventComments(BaseModel):
    comment_id = fields.IntField(pk=True)
    event = fields.ForeignKeyField('models.Events', related_name='comments')
    user = fields.ForeignKeyField('models.Users', related_name='comments')
    content = fields.TextField()

    class Meta:
        table = "event_comments"

class Notifications(BaseModel):
    notification_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='notifications')
    club = fields.ForeignKeyField('models.Clubs', related_name='club_notifications', null=True)
    event = fields.ForeignKeyField('models.Events', related_name='event_notifications', null=True)
    message = fields.CharField(max_length=255)
    is_read = fields.BooleanField(default=False)

    class Meta:
        table = "notifications"