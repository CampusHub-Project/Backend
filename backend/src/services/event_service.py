from src.models import Events, Clubs, EventParticipation, ParticipationStatus, UserRole
from tortoise.exceptions import DoesNotExist
from src.services.notification_service import NotificationService
from datetime import datetime
from tortoise.expressions import Q

class EventService:

    @staticmethod
    async def create_event(user_ctx, data):
        club_id = data.get("club_id")
        club = await Clubs.get_or_none(club_id=club_id)
        if not club or club.is_deleted:
            return {"error": "Club not found"}, 404

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
    async def delete_event(user_ctx, event_id: int):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            is_admin = user_ctx["role"] == UserRole.ADMIN
            is_president = event.club.president_id == user_ctx["sub"]
            
            if not (is_admin or is_president):
                return {"error": "Unauthorized"}, 403

            event.is_deleted = True
            event.deleted_at = datetime.utcnow()
            await event.save()
            return {"message": "Event deleted"}, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404

    @staticmethod
    async def get_event_detail(event_id: int):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            if event.is_deleted: return {"error": "Event not found"}, 404
            
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
    async def get_events(page: int = 1, limit: int = 20, search: str = None, date_filter: str = None):
        """Filtreli ve Sayfalı Etkinlik Listesi"""
        
        # 1. Temel Sorgu: Silinmemiş etkinlikler VE Onaylı Kulüpler
        query = Events.filter(is_deleted=False, club__status="active")

        # 2. Arama Filtresi (Başlık VEYA Açıklamada ara)
        if search:
            query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
        # 3. Tarih Filtresi (Seçilen tarihten sonrakiler)
        if date_filter:
            query = query.filter(event_date__gte=date_filter)

        # Toplam sayıyı al (Pagination metadatasında göstermek için)
        total_count = await query.count()

        # 4. Sayfalama (Offset/Limit)
        offset = (page - 1) * limit
        events = await query.prefetch_related("club").order_by("event_date").offset(offset).limit(limit)
        
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
            
        return {
            "events": result,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit
            }
        }, 200

    @staticmethod
    async def join_event(user_ctx, event_id: int):
        try:
            event = await Events.get(event_id=event_id)
            if event.is_deleted: return {"error": "Event not found"}, 404
            
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

    @staticmethod
    async def leave_event(user_ctx, event_id: int):
        deleted_count = await EventParticipation.filter(user_id=user_ctx["sub"], event_id=event_id).delete()
        if deleted_count == 0:
            return {"error": "You are not participating in this event"}, 400
        return {"message": "Successfully left the event"}, 200

    @staticmethod
    async def remove_participant(user_ctx, event_id: int, target_user_id: int):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            is_admin = user_ctx["role"] == UserRole.ADMIN
            is_president = event.club.president_id == user_ctx["sub"]
            
            if not (is_admin or is_president):
                return {"error": "Unauthorized"}, 403

            deleted_count = await EventParticipation.filter(user_id=target_user_id, event_id=event_id).delete()
            if deleted_count == 0:
                return {"error": "User is not a participant"}, 404
            return {"message": "Participant removed"}, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404