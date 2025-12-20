from src.models import EventParticipation, ParticipationStatus, Users, EventComments, ClubFollowers
from tortoise.exceptions import DoesNotExist

class UserService:

    @staticmethod
    async def get_user_history(user_id: int):
        participations = await EventParticipation.filter(
            user_id=user_id, 
            status=ParticipationStatus.GOING
        ).prefetch_related("event", "event__club").order_by("-created_at")
        
        history = []
        for p in participations:
            if p.event:
                history.append({
                    "event_id": p.event.event_id,
                    "title": p.event.title,
                    "date": str(p.event.event_date),
                    "club_name": p.event.club.club_name if p.event.club else "Bilinmiyor",
                    "joined_at": str(p.created_at)
                })
        
        return {"history": history}, 200

    @staticmethod
    async def get_user_profile(user_id: int):
        try:
            user = await Users.get(user_id=user_id)
            
            # Katıldığı Etkinlikler
            participations = await EventParticipation.filter(user_id=user_id).prefetch_related("event", "event__club")
            participated_events = [
                {
                    "id": p.event.event_id,
                    "title": p.event.title,
                    "date": str(p.event.event_date),
                    "club_name": p.event.club.club_name if p.event.club else "Unknown"
                } for p in participations if p.event
            ]
            
            # Takip Edilen Kulüpler
            followed = await ClubFollowers.filter(user_id=user_id).prefetch_related("club")
            clubs = [{"id": f.club.club_id, "name": f.club.club_name} for f in followed if f.club]
            
            return {
                "profile": {
                    "id": user.user_id,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}",
                    "department": user.department,
                    "role": user.role,
                    "profile_photo": user.profile_image,
                    "bio": user.bio,
                    "interests": user.interests
                },
                "activities": {
                    "participated_events": participated_events,
                    "followed_clubs": clubs
                }
            }, 200
        except DoesNotExist:
            return {"error": "User not found"}, 404

    @staticmethod
    async def update_profile(user_id: int, data: dict):
        try:
            user = await Users.get(user_id=user_id)
            
            # İsim güncelleme isteği gelirse ayır
            if "full_name" in data:
                names = data["full_name"].strip().split(" ")
                user.first_name = names[0]
                user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
            
            if "bio" in data: user.bio = data["bio"]
            if "interests" in data: user.interests = data["interests"]
            if "department" in data: user.department = data["department"]
            if "profile_photo" in data: user.profile_image = data["profile_photo"]
                
            await user.save()
            return {
                "message": "Profile updated",
                "profile": {
                    "full_name": f"{user.first_name} {user.last_name}",
                    "bio": user.bio
                }
            }, 200
        except DoesNotExist:
            return {"error": "User not found"}, 404