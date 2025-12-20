from src.models import Clubs, ClubFollowers, UserRole
from tortoise.exceptions import DoesNotExist
from datetime import datetime

class ClubService:

    @staticmethod
    async def create_club(user_ctx, data):
        # YENİ MANTIK: Rol kontrolünü kaldırdık.
        # Admin oluşturursa -> ACTIVE
        # Öğrenci oluşturursa -> PENDING (Onay Bekliyor)
        
        status = "active" if user_ctx["role"] == UserRole.ADMIN else "pending"

        try:
            club = await Clubs.create(
                club_name=data.get("name"),
                description=data.get("description"),
                logo_url=data.get("image_url"),
                president_id=user_ctx["sub"],
                created_by_id=user_ctx["sub"],
                status=status  # <-- Status eklendi
            )
            
            msg = "Club created successfully" if status == "active" else "Club application submitted for approval"
            return {"message": msg, "club": {"id": club.club_id, "name": club.club_name, "status": status}}, 201
            
        except Exception as e:
            return {"error": str(e)}, 400

    # --- YENİ METOD: KULÜP ONAYLAMA ---
    @staticmethod
    async def approve_club(user_ctx, club_id: int):
        # Sadece Admin onaylayabilir
        if user_ctx["role"] != UserRole.ADMIN:
            return {"error": "Unauthorized"}, 403
            
        try:
            club = await Clubs.get(club_id=club_id)
            if club.is_deleted: return {"error": "Club not found"}, 404
            
            if club.status == "active":
                return {"message": "Club is already active"}, 400
                
            club.status = "active"
            await club.save()
            return {"message": f"Club '{club.club_name}' approved successfully"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    # ... Diğer metodlar (delete_club, get_all_clubs vb.) AYNI KALACAK ...
    # Ancak get_all_clubs içinde sadece 'active' olanları getirmek isteyebilirsiniz
    # Şimdilik hepsini getiriyoruz ki admin bekleyenleri de görsün.
    # Frontend tarafında filtreleme yapılabilir veya buraya parametre eklenebilir.
    
    @staticmethod
    async def delete_club(user_ctx, club_id: int):
        if user_ctx["role"] != UserRole.ADMIN:
            return {"error": "Unauthorized"}, 403
        try:
            club = await Clubs.get(club_id=club_id)
            club.is_deleted = True
            club.deleted_at = datetime.utcnow()
            await club.save()
            return {"message": "Club deleted successfully"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def get_all_clubs():
        # Sadece silinmemişleri getir
        clubs = await Clubs.filter(is_deleted=False).all()
        
        clubs_list = []
        for club in clubs:
            clubs_list.append({
                "id": club.club_id,
                "name": club.club_name,
                "description": club.description,
                "image_url": club.logo_url,
                "status": club.status, # Durumu da frontend görsün
                "created_at": str(club.created_at)
            })
        
        return {"clubs": clubs_list}, 200

    @staticmethod
    async def get_club_details(club_id: int):
        try:
            club = await Clubs.get(club_id=club_id)
            if club.is_deleted: return {"error": "Club not found"}, 404

            await club.fetch_related("events")
            events_list = []
            for event in club.events:
                if not event.is_deleted:
                    events_list.append({
                        "id": event.event_id,
                        "title": event.title,
                        "date": str(event.event_date),
                        "location": event.location,
                        "image_url": event.image_url,
                        "capacity": event.quota
                    })
            
            return {
                "club": {
                    "id": club.club_id,
                    "name": club.club_name,
                    "description": club.description,
                    "image_url": club.logo_url,
                    "status": club.status,
                    "events": events_list
                }
            }, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def follow_club(user_ctx, club_id: int):
        try:
            club = await Clubs.get(club_id=club_id)
            if club.is_deleted: return {"error": "Club not found"}, 404
            
            # Sadece aktif kulüpler takip edilebilir
            if club.status != "active":
                return {"error": "Cannot follow pending club"}, 400

            exists = await ClubFollowers.filter(user_id=user_ctx["sub"], club_id=club_id).exists()
            if exists:
                return {"message": "Already following"}, 400
            
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
            
            if not (is_admin or is_president):
                return {"error": "Unauthorized"}, 403

            deleted_count = await ClubFollowers.filter(user_id=target_user_id, club_id=club_id).delete()
            if deleted_count == 0:
                return {"error": "User is not a follower"}, 404
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