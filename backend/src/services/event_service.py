import json
from src.models import Events, Clubs, EventParticipation, ParticipationStatus, UserRole
from tortoise.exceptions import DoesNotExist
from src.services.notification_service import NotificationService
from datetime import datetime
from tortoise.expressions import Q
from src.config import logger # <--- Logger

class EventService:

    @staticmethod
    async def create_event(user_ctx, data):
        club_id = data.get("club_id")
        club = await Clubs.get_or_none(club_id=club_id)
        if not club or club.is_deleted:
            return {"error": "Club not found"}, 404

        if user_ctx["role"] != UserRole.ADMIN and club.president_id != user_ctx["sub"]:
            logger.warning(f"Unauthorized Event Creation Attempt by {user_ctx['sub']} for Club {club_id}")
            return {"error": "Unauthorized."}, 403

        # --- GÜNCELLEME: Kapasite Kontrolü ---
        capacity = data.get("capacity", 0)
        try:
            capacity = int(capacity)
        except:
            return {"error": "Capacity must be a number"}, 400
            
        if capacity <= 0:
            return {"error": "Capacity must be greater than 0"}, 400
        # -------------------------------------

        event = await Events.create(
            title=data.get("title"),
            description=data.get("description"),
            event_date=data.get("date"),
            location=data.get("location"),
            quota=capacity,
            club_id=club_id, # club_id yukarıdaki koddan geliyor
            image_url=data.get("image_url"),
            created_by_id=user_ctx["sub"]
        )
        
        logger.info(f"Event Created: '{event.title}' (ID: {event.event_id}) for Club '{club.club_name}'")

        await NotificationService.notify_followers(club.club_id, club.club_name, event.title)
        return {"message": "Event created", "event_id": event.event_id}, 201

    @staticmethod
    async def delete_event(user_ctx, event_id: int):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            is_admin = user_ctx["role"] == UserRole.ADMIN
            is_president = event.club.president_id == user_ctx["sub"]
            
            if not (is_admin or is_president): return {"error": "Unauthorized"}, 403

            event.is_deleted = True
            event.deleted_at = datetime.utcnow()
            await event.save()
            
            logger.info(f"Event Deleted: {event.title} (ID: {event_id}) by {user_ctx['sub']}")
            return {"message": "Event deleted"}, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404

    @staticmethod
    async def get_event_detail(event_id: int, user_ctx=None): # user_ctx eklendi
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            if event.is_deleted: return {"error": "Event not found"}, 404
            
            participant_count = await EventParticipation.filter(
                event_id=event_id, status=ParticipationStatus.GOING
            ).count()

            # --- GÜNCELLEME: Kullanıcı katılmış mı? ---
            is_joined = False
            if user_ctx:
                is_joined = await EventParticipation.filter(
                    event_id=event_id, 
                    user_id=user_ctx["sub"], 
                    status=ParticipationStatus.GOING
                ).exists()
            # ------------------------------------------
            
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
                    "participant_count": participant_count,
                    "is_joined": is_joined # Frontend buna bakıp butonu değiştirecek
                }
            }, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404

    @staticmethod
    async def update_event(user_ctx, event_id: int, data: dict):
        try:
            event = await Events.get(event_id=event_id).prefetch_related("club")
            
            is_admin = user_ctx["role"] == UserRole.ADMIN
            is_president = event.club.president_id == user_ctx["sub"]

            if not (is_admin or is_president):
                return {"error": "Unauthorized"}, 403

            if "title" in data: event.title = data["title"]
            if "description" in data: event.description = data["description"]
            if "date" in data: event.event_date = data["date"]
            if "location" in data: event.location = data["location"]
            if "capacity" in data: 
                cap = int(data["capacity"])
                if cap > 0: event.quota = cap

            await event.save()
            return {"message": "Event updated successfully"}, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404

    @staticmethod
    async def get_events(redis, page: int = 1, limit: int = 20, search: str = None, date_filter: str = None):
        cache_key = f"events:page:{page}:lim:{limit}:s:{search}:d:{date_filter}"
        
        if redis:
            cached_data = await redis.get(cache_key)
            if cached_data: return json.loads(cached_data), 200

        query = Events.filter(is_deleted=False, club__status="active")

        if search:
            query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
        if date_filter:
            query = query.filter(event_date__gte=date_filter)

        total_count = await query.count()

        offset = (page - 1) * limit
        events = await query.prefetch_related("club").order_by("event_date").offset(offset).limit(limit)
        
        result_list = [{
            "id": e.event_id,
            "title": e.title,
            "description": e.description,
            "date": str(e.event_date),
            "club_name": e.club.club_name if e.club else "Unknown",
            "location": e.location,
            "image_url": e.image_url,
            "capacity": e.quota
        } for e in events]
            
        response_data = {
            "events": result_list,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit
            }
        }

        if redis: await redis.set(cache_key, json.dumps(response_data), ex=60)

        return response_data, 200

    @staticmethod
    async def join_event(user_ctx, event_id: int):
        try:
            event = await Events.get(event_id=event_id)
            if event.is_deleted: return {"error": "Event not found"}, 404
            
            current_count = await EventParticipation.filter(event_id=event_id, status=ParticipationStatus.GOING).count()
            if event.quota > 0 and current_count >= event.quota:
                logger.info(f"Join failed (Full): Event {event_id}, User {user_ctx['sub']}")
                return {"error": "Event is full"}, 400

            exists = await EventParticipation.filter(user_id=user_ctx["sub"], event_id=event_id).exists()
            if exists: return {"message": "Already joined"}, 400

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
            
            if not (is_admin or is_president): return {"error": "Unauthorized"}, 403

            deleted_count = await EventParticipation.filter(user_id=target_user_id, event_id=event_id).delete()
            if deleted_count == 0: return {"error": "User is not a participant"}, 404
            
            logger.info(f"Participant {target_user_id} removed from Event {event_id} by {user_ctx['sub']}")
            return {"message": "Participant removed"}, 200
        except DoesNotExist:
            return {"error": "Event not found"}, 404