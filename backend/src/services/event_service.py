from src.models import Events, Clubs, EventParticipation, ParticipationStatus, UserRole
from tortoise.exceptions import DoesNotExist
from src.services.notification_service import NotificationService

class EventService:

    @staticmethod
    async def create_event(user_ctx, data):
        club_id = data.get("club_id")
        club = await Clubs.get_or_none(club_id=club_id)
        if not club:
            return {"error": "Club not found"}, 404

        # Yetki Kontrolü: Admin veya o kulübün başkanı
        if user_ctx["role"] != UserRole.ADMIN and club.president_id != user_ctx["sub"]:
            return {"error": "Unauthorized."}, 403

        event = await Events.create(
            title=data.get("title"),
            description=data.get("description"),
            event_date=data.get("date"),
            location=data.get("location"),
            quota=data.get("capacity", 0),
            club_id=club_id,
            image_url=data.get("image_url"),
            created_by_id=user_ctx["sub"]
        )

        await NotificationService.notify_followers(club.club_id, club.club_name, event.title)
        
        return {"message": "Event created", "event_id": event.event_id}, 201

    @staticmethod
    async def get_event_detail(event_id: int):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            participant_count = await EventParticipation.filter(
                event_id=event_id, status=ParticipationStatus.GOING
            ).count()
            
            return {
                "event": {
                    "id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "date": str(event.event_date),
                    "location": event.location,
                    "capacity": event.quota,
                    "image_url": event.image_url,
                    "club_name": event.club.club_name if event.club else "Unknown",
                    "club_id": event.club.club_id if event.club else None,
                    "participant_count": participant_count
                }
            }, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404
        
    @staticmethod
    async def get_events():
        events = await Events.filter(is_deleted=False).prefetch_related("club").order_by("event_date")
        
        result = []
        for e in events:
            result.append({
                "id": e.event_id,
                "title": e.title,
                "description": e.description,
                "date": str(e.event_date),
                "club_name": e.club.club_name if e.club else "Unknown",
                "location": e.location,
                "image_url": e.image_url,
                "capacity": e.quota
            })
        return {"events": result}, 200

    @staticmethod
    async def join_event(user_ctx, event_id: int):
        try:
            event = await Events.get(event_id=event_id)
            
            current_count = await EventParticipation.filter(event_id=event_id, status=ParticipationStatus.GOING).count()
            if event.quota > 0 and current_count >= event.quota:
                return {"error": "Event is full"}, 400

            exists = await EventParticipation.filter(user_id=user_ctx["sub"], event_id=event_id).exists()
            if exists:
                return {"message": "Already joined"}, 400

            await EventParticipation.create(
                user_id=user_ctx["sub"],
                event_id=event_id,
                status=ParticipationStatus.GOING
            )
            return {"message": "Successfully joined"}, 200
            
        except DoesNotExist:
            return {"error": "Event not found"}, 404