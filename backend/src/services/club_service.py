from src.models import Clubs, ClubFollowers, UserRole
from tortoise.exceptions import DoesNotExist

class ClubService:

    @staticmethod
    async def create_club(user_ctx, data):
        # Yetki Kontrolü: Sadece 'admin' rolü kulüp açabilir
        if user_ctx["role"] != UserRole.ADMIN:
            return {"error": "Unauthorized. Only admins can create clubs."}, 403

        # Kulübü oluştur
        try:
            club = await Clubs.create(
                name=data.get("name"),
                description=data.get("description"),
                image_url=data.get("image_url"),
                admin_id=user_ctx["sub"]
            )
            return {"message": "Club created", "club": {"id": club.id, "name": club.name}}, 201
        except Exception as e:
            return {"error": str(e)}, 400

    @staticmethod
    async def get_all_clubs():
        # Tüm kulüpleri getir ve dictionary'ye çevir
        clubs = await Clubs.all()
        
        # Convert model objects to dictionaries
        clubs_list = []
        for club in clubs:
            clubs_list.append({
                "id": club.id,
                "name": club.name,
                "description": club.description,
                "image_url": club.image_url,
                "created_at": str(club.created_at)
            })
        
        return {"clubs": clubs_list}, 200

    @staticmethod
    async def get_club_details(club_id: int):
        try:
            club = await Clubs.get(id=club_id)
            # İlişkili etkinlikleri de çekelim
            await club.fetch_related("events")
            
            # Convert events to dictionaries
            events_list = []
            for event in club.events:
                events_list.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": str(event.date),
                    "location": event.location,
                    "image_url": event.image_url,
                    "capacity": event.capacity
                })
            
            return {
                "club": {
                    "id": club.id,
                    "name": club.name,
                    "description": club.description,
                    "image_url": club.image_url,
                    "events": events_list
                }
            }, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404

    @staticmethod
    async def follow_club(user_ctx, club_id: int):
        try:
            # Kulüp var mı?
            club = await Clubs.get(id=club_id)
            
            # Zaten takip ediyor mu?
            exists = await ClubFollowers.filter(user_id=user_ctx["sub"], club_id=club_id).exists()
            if exists:
                return {"message": "Already following"}, 400
            
            await ClubFollowers.create(user_id=user_ctx["sub"], club_id=club_id)
            return {"message": f"You are now following {club.name}"}, 200
        except DoesNotExist:
            return {"error": "Club not found"}, 404
        
    @staticmethod
    async def get_my_clubs(user_ctx):
        # Eğer sistem yöneticisi ise (ADMIN) tüm kulüpleri getirelim
        if user_ctx["role"] == UserRole.ADMIN:
            clubs = await Clubs.all()
        else:
            # Sadece kendi yönettiği kulüpleri getir
            clubs = await Clubs.filter(admin_id=user_ctx["sub"])
        
        # Convert to dictionaries
        clubs_list = []
        for club in clubs:
            clubs_list.append({
                "id": club.id,
                "name": club.name,
                "description": club.description,
                "image_url": club.image_url
            })
            
        return {"clubs": clubs_list}, 200