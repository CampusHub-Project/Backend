from src.models import Events, Clubs, EventParticipation, ParticipationStatus, UserRole
from tortoise.exceptions import DoesNotExist
from datetime import datetime
from src.services.notification_service import NotificationService

class EventService:

    @staticmethod
    async def create_event(user_ctx, data):
        club_id = data.get("club_id")
        
        # Kulüp kontrolü
        club = await Clubs.get_or_none(id=club_id)
        if not club:
            return {"error": "Club not found"}, 404

        # Yetki Kontrolü
        if user_ctx["role"] != UserRole.ADMIN and club.admin_id != user_ctx["sub"]:
            return {"error": "Unauthorized. You are not the admin of this club."}, 403

        event = await Events.create(
            title=data.get("title"),
            description=data.get("description"),
            date=data.get("date"),
            location=data.get("location"),
            capacity=data.get("capacity", 0),
            club_id=club_id,
            image_url=data.get("image_url")
        )

        await NotificationService.notify_followers(club.id, club.name, event.title)
        
        return {"message": "Event created", "event_id": event.id}, 201

    @staticmethod
    async def get_event_detail(event_id: int):
        """Get detailed information about a single event"""
        try:
            event = await Events.get(id=event_id).prefetch_related("club")
            
            # Count participants
            participant_count = await EventParticipation.filter(
                event_id=event_id,
                status=ParticipationStatus.GOING
            ).count()
            
            return {
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": str(event.date),
                    "location": event.location,
                    "capacity": event.capacity,
                    "image_url": event.image_url,
                    "club_name": event.club.name if event.club else "Unknown",
                    "club_id": event.club.id if event.club else None,
                    "participant_count": participant_count,
                    "created_at": str(event.created_at)
                }
            }, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404
        
    @staticmethod
    async def get_events():
        # Tüm etkinlikleri getir
        events = await Events.all().prefetch_related("club").order_by("date")
        
        result = []
        for e in events:
            result.append({
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "date": str(e.date),
                "club_name": e.club.name if e.club else "Bilinmiyor",
                "location": e.location,
                "image_url": e.image_url,
                "capacity": e.capacity
            })
        return {"events": result}, 200

    @staticmethod
    async def join_event(user_ctx, event_id: int):
        try:
            event = await Events.get(id=event_id)
            
            # Kapasite kontrolü
            current_count = await EventParticipation.filter(event_id=event_id, status=ParticipationStatus.GOING).count()
            if event.capacity > 0 and current_count >= event.capacity:
                return {"error": "Event is full"}, 400

            # Zaten katıldı mı?
            exists = await EventParticipation.filter(user_id=user_ctx["sub"], event_id=event_id).exists()
            if exists:
                return {"message": "Already joined"}, 400

            await EventParticipation.create(
                user_id=user_ctx["sub"],
                event_id=event_id,
                status=ParticipationStatus.GOING
            )
            return {"message": "Successfully joined the event"}, 200
            
        except DoesNotExist:
            return {"error": "Event not found"}, 404