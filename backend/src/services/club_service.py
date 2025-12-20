from src.models import Clubs, ClubFollowers, UserRole
from tortoise.exceptions import DoesNotExist

class ClubService:

    @staticmethod
    async def create_club(user_ctx, data):
        if user_ctx["role"] != UserRole.ADMIN:
            return {"error": "Unauthorized. Only admins can create clubs."}, 403

        try:
            club = await Clubs.create(
                club_name=data.get("name"),
                description=data.get("description"),
                logo_url=data.get("image_url"),
                president_id=user_ctx["sub"],
                created_by_id=user_ctx["sub"]
            )
            return {"message": "Club created", "club": {"id": club.club_id, "name": club.club_name}}, 201
        except Exception as e:
            return {"error": str(e)}, 400

    @staticmethod
    async def get_all_clubs():
        clubs = await Clubs.filter(is_deleted=False).all()
        
        clubs_list = []
        for club in clubs:
            clubs_list.append({
                "id": club.club_id,
                "name": club.club_name,
                "description": club.description,
                "image_url": club.logo_url,
                "created_at": str(club.created_at)
            })
        
        return {"clubs": clubs_list}, 200

    @staticmethod
    async def get_club_details(club_id: int):
        try:
            club = await Clubs.get(club_id=club_id)
            await club.fetch_related("events")
            
            events_list = []
            for event in club.events:
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
                    "events": events_list
                }
            }, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def follow_club(user_ctx, club_id: int):
        try:
            club = await Clubs.get(club_id=club_id)
            exists = await ClubFollowers.filter(user_id=user_ctx["sub"], club_id=club_id).exists()
            if exists:
                return {"message": "Already following"}, 400
            
            await ClubFollowers.create(user_id=user_ctx["sub"], club_id=club_id)
            return {"message": f"You are now following {club.club_name}"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404
            
    @staticmethod
    async def get_my_clubs(user_ctx):
        if user_ctx["role"] == UserRole.ADMIN:
            clubs = await Clubs.all()
        else:
            clubs = await Clubs.filter(president_id=user_ctx["sub"])
        
        clubs_list = [{"id": c.club_id, "name": c.club_name, "image_url": c.logo_url} for c in clubs]
        return {"clubs": clubs_list}, 200