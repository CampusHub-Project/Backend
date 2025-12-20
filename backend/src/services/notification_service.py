from src.models import Notifications, ClubFollowers
from tortoise.exceptions import DoesNotExist

class NotificationService:

    @staticmethod
    async def create_notification(user_id: int, message: str, club_id: int = None, event_id: int = None):
        await Notifications.create(
            user_id=user_id, 
            message=message,
            club_id=club_id,
            event_id=event_id
        )

    @staticmethod
    async def notify_followers(club_id: int, club_name: str, event_title: str):
        followers = await ClubFollowers.filter(club_id=club_id).all()
        
        message = f"📢 '{club_name}' yeni bir etkinlik paylaştı: {event_title}"
        for f in followers:
            await Notifications.create(
                user_id=f.user_id, 
                message=message,
                club_id=club_id
            )

    @staticmethod
    async def get_my_notifications(user_id: int):
        notifs = await Notifications.filter(user_id=user_id).order_by("-is_read", "-created_at")
        return {"notifications": list(notifs)}, 200

    @staticmethod
    async def mark_as_read(notif_id: int, user_id: int):
        try:
            # notification_id alanına göre sorgu
            notif = await Notifications.get(notification_id=notif_id, user_id=user_id)
            notif.is_read = True
            await notif.save()
            return {"message": "Marked as read"}, 200
        except DoesNotExist:
            return {"error": "Notification not found"}, 404