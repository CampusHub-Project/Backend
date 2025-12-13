from tortoise import fields, models
from enum import Enum

# --- ENUM Sınıfları (Sabit Seçenekler) ---

class UserRole(str, Enum):
    STUDENT = "student"
    CLUB_ADMIN = "club_admin"
    ADMIN = "admin"

class ParticipationStatus(str, Enum):
    GOING = "going"
    INTERESTED = "interested"

# --- MODELLER (Tablolar) ---

class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=100)
    role = fields.CharEnumField(UserRole, default=UserRole.STUDENT)
    
    # NEW FIELDS for profile
    profile_photo = fields.CharField(max_length=500, null=True)  # URL to profile photo
    bio = fields.TextField(null=True)  # User bio/about me
    interests = fields.TextField(null=True)  # User interests (comma-separated or JSON)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # İlişkiler (Reverse relations)
    clubs_managed: fields.ReverseRelation["Clubs"]
    participations: fields.ReverseRelation["EventParticipation"]
    notifications: fields.ReverseRelation["Notifications"]

    class Meta:
        table = "users"

class Clubs(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    image_url = fields.CharField(max_length=255, null=True)
    admin = fields.ForeignKeyField('models.Users', related_name='clubs_managed')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    events: fields.ReverseRelation["Events"]

    class Meta:
        table = "clubs"

class ClubFollowers(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='following')
    club = fields.ForeignKeyField('models.Clubs', related_name='followers')
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "club_followers"
        unique_together = ("user", "club")

class Events(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=150)
    description = fields.TextField()
    date = fields.DatetimeField()
    location = fields.CharField(max_length=255)
    image_url = fields.CharField(max_length=255, null=True)
    capacity = fields.IntField(default=0)
    club = fields.ForeignKeyField('models.Clubs', related_name='events')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "events"

class EventParticipation(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='event_participations')
    event = fields.ForeignKeyField('models.Events', related_name='participants')
    status = fields.CharEnumField(ParticipationStatus, default=ParticipationStatus.GOING)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_participation"
        unique_together = ("user", "event")

class EventComments(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='comments')
    event = fields.ForeignKeyField('models.Events', related_name='comments')
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_comments"

# NEW MODEL for Event Reactions (likes/dislikes)
class EventReactions(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='reactions')
    event = fields.ForeignKeyField('models.Events', related_name='reactions')
    is_like = fields.BooleanField()  # True = like, False = dislike
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_reactions"
        unique_together = ("user", "event")

class Notifications(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='user_notifications')
    message = fields.CharField(max_length=255)
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"