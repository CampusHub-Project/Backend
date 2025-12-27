import json
from src.models import Clubs, ClubFollowers, UserRole
from tortoise.exceptions import DoesNotExist
from datetime import datetime
from src.config import logger

class ClubService:

    @staticmethod
    async def create_club(user_ctx, data, redis=None):
        status = "active" if user_ctx["role"] == UserRole.ADMIN else "pending"

        try:
            club = await Clubs.create(
                club_name=data.get("name"),
                description=data.get("description"),
                logo_url=data.get("image_url"),
                president_id=user_ctx["sub"],
                created_by_id=user_ctx["sub"],
                status=status
            )
            
            msg = "Club created successfully"
            if status == "active":
                logger.info(f"Club Created (Active) by Admin: {club.club_name}")
                if redis: await redis.delete("clubs:all_active")
            else:
                logger.info(f"Club Application Submitted: {club.club_name} by User {user_ctx['sub']}")
                msg = "Club application submitted for approval"

            return {"message": msg, "club": {"id": club.club_id, "name": club.club_name, "status": status}}, 201
            
        except Exception as e:
            logger.error(f"Club Creation Error: {str(e)}")
            return {"error": str(e)}, 400

    @staticmethod
    async def approve_club(user_ctx, club_id: int, redis=None):
        if user_ctx["role"] != UserRole.ADMIN:
            logger.warning(f"Unauthorized Club Approval Attempt by User {user_ctx['sub']}")
            return {"error": "Unauthorized"}, 403
            
        try:
            club = await Clubs.get(club_id=club_id)
            if club.is_deleted: return {"error": "Club not found"}, 404
            
            if club.status == "active":
                return {"message": "Club is already active"}, 400
                
            club.status = "active"
            await club.save()
            
            logger.info(f"Club Approved: {club.club_name} by Admin {user_ctx['sub']}")
            
            if redis: await redis.delete("clubs:all_active")

            return {"message": f"Club '{club.club_name}' approved successfully"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def delete_club(user_ctx, club_id: int, redis=None):
        if user_ctx["role"] != UserRole.ADMIN:
            return {"error": "Unauthorized"}, 403
        try:
            club = await Clubs.get(club_id=club_id)
            club.is_deleted = True
            club.deleted_at = datetime.utcnow()
            await club.save()
            
            logger.info(f"Club Deleted: {club.club_name} (ID: {club_id})")
            
            if redis: await redis.delete("clubs:all_active")

            return {"message": "Club deleted successfully"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def get_all_clubs(redis=None):
        cache_key = "clubs:all_active"
        if redis:
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data), 200
        
        clubs = await Clubs.filter(is_deleted=False, status="active").all()
        
        clubs_list = [{
            "id": c.club_id,
            "name": c.club_name,
            "description": c.description,
            "image_url": c.logo_url,
            "status": c.status,
            "created_at": str(c.created_at)
        } for c in clubs]
            
        response_data = {"clubs": clubs_list}
        
        if redis: await redis.set(cache_key, json.dumps(response_data), ex=300)
        
        return response_data, 200

    @staticmethod
    async def get_club_details(club_id: int, user_ctx=None): 
        try:
            club = await Clubs.get(club_id=club_id).prefetch_related("events") 
            if club.is_deleted: return {"error": "Club not found"}, 404

            followers_list = []
            is_authorized_viewer = False
            
            if user_ctx:
                is_admin = user_ctx["role"] == UserRole.ADMIN
                is_president = club.president_id == user_ctx["sub"]
                
                if is_admin or is_president:
                    is_authorized_viewer = True
                    followers = await ClubFollowers.filter(club_id=club_id).prefetch_related("user")
                    followers_list = [{
                        "user_id": f.user.user_id,
                        "full_name": f"{f.user.first_name} {f.user.last_name}",
                        "email": f.user.email
                    } for f in followers if f.user]

            events_list = [{
                "id": e.event_id,
                "title": e.title,
                "date": str(e.event_date),
                "location": e.location,
                "image_url": e.image_url,
                "capacity": e.quota
            } for e in club.events if not e.is_deleted]
            
            return {
                "club": {
                    "id": club.club_id,
                    "name": club.club_name,
                    "description": club.description,
                    "image_url": club.logo_url,
                    "status": club.status,
                    "president_id": club.president_id, 
                    "events": events_list,
                    "members": followers_list if is_authorized_viewer else [] 
                }
            }, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def follow_club(user_ctx, club_id: int):
        if user_ctx["role"] == UserRole.ADMIN:
             return {"error": "Admins cannot join clubs"}, 400

        try:
            club = await Clubs.get(club_id=club_id)
            if club.is_deleted: return {"error": "Club not found"}, 404
            
            if club.status != "active":
                return {"error": "Cannot follow pending club"}, 400

            exists = await ClubFollowers.filter(user_id=user_ctx["sub"], club_id=club_id).exists()
            if exists: return {"message": "Already following"}, 400
            
            await ClubFollowers.create(user_id=user_ctx["sub"], club_id=club_id)
            return {"message": f"You are now following {club.club_name}"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def leave_club(user_ctx, club_id: int):
        deleted_count = await ClubFollowers.filter(user_id=user_ctx["sub"], club_id=club_id).delete()
        if deleted_count == 0:
            return {"error": "You are not following this club"}, 400
        return {"message": "Successfully unfollowed"}, 200

    @staticmethod
    async def remove_follower(user_ctx, club_id: int, target_user_id: int):
        try:
            club = await Clubs.get(club_id=club_id)
            is_admin = user_ctx["role"] == UserRole.ADMIN
            is_president = club.president_id == user_ctx["sub"]
            
            if not (is_admin or is_president): return {"error": "Unauthorized"}, 403

            deleted_count = await ClubFollowers.filter(user_id=target_user_id, club_id=club_id).delete()
            if deleted_count == 0: return {"error": "User is not a follower"}, 404
            
            logger.info(f"User {target_user_id} removed from Club {club_id} by {user_ctx['sub']}")
            return {"message": "User removed from club"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def get_my_clubs(user_ctx):
        if user_ctx["role"] == UserRole.ADMIN:
            clubs = await Clubs.filter(is_deleted=False).all()
        else:
            clubs = await Clubs.filter(president_id=user_ctx["sub"], is_deleted=False)
        
        clubs_list = [{"id": c.club_id, "name": c.club_name, "image_url": c.logo_url, "status": c.status} for c in clubs]
        return {"clubs": clubs_list}, 200