from src.models import Notifications, ClubFollowers
from tortoise.exceptions import DoesNotExist

class NotificationService:

    @staticmethod
    async def create_notification(user_id: int, message: str):
        await Notifications.create(user_id=user_id, message=message)

    @staticmethod
    async def notify_followers(club_id: int, club_name: str, event_title: str):
        # Kulübü takip eden herkesi bul
        followers = await ClubFollowers.filter(club_id=club_id).all()
        
        # Her biri için bildirim oluştur
        message = f"📢 '{club_name}' kulübü yeni bir etkinlik paylaştı: {event_title}"
        for f in followers:
            await Notifications.create(user_id=f.user_id, message=message)

    @staticmethod
    async def get_my_notifications(user_id: int):
        # Okunmamışları en üstte göster
        notifs = await Notifications.filter(user_id=user_id).order_by("-is_read", "-created_at")
        return {"notifications": list(notifs)}, 200

    @staticmethod
    async def mark_as_read(notif_id: int, user_id: int):
        try:
            notif = await Notifications.get(id=notif_id, user_id=user_id)
            notif.is_read = True
            await notif.save()
            return {"message": "Marked as read"}, 200
        except DoesNotExist:
            return {"error": "Notification not found"}, 404