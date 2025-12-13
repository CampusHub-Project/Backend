from src.models import EventParticipation, ParticipationStatus, Users, EventComments, ClubFollowers
from tortoise.exceptions import DoesNotExist
from datetime import datetime

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
                    "event_id": p.event.id,
                    "title": p.event.title,
                    "date": str(p.event.date),
                    "club_name": p.event.club.name if p.event.club else "Bilinmiyor",
                    "joined_at": str(p.created_at)
                })
        
        return {"history": history}, 200

    @staticmethod
    async def get_user_profile(user_id: int):
        """Get complete user profile with all activities"""
        try:
            user = await Users.get(id=user_id)
            
            # Get participated events
            participations = await EventParticipation.filter(
                user_id=user_id
            ).prefetch_related("event", "event__club").order_by("-created_at")
            
            participated_events = []
            for p in participations:
                if p.event:
                    participated_events.append({
                        "id": p.event.id,
                        "title": p.event.title,
                        "date": str(p.event.date),
                        "club_name": p.event.club.name if p.event.club else "Unknown"
                    })
            
            # Get commented events
            comments = await EventComments.filter(
                user_id=user_id
            ).prefetch_related("event").order_by("-created_at")
            
            commented_events = []
            seen_events = set()
            for c in comments:
                if c.event and c.event.id not in seen_events:
                    commented_events.append({
                        "id": c.event.id,
                        "title": c.event.title,
                        "comment": c.content
                    })
                    seen_events.add(c.event.id)
            
            # Get followed clubs
            followed_clubs = await ClubFollowers.filter(
                user_id=user_id
            ).prefetch_related("club")
            
            clubs = [{"id": f.club.id, "name": f.club.name} for f in followed_clubs if f.club]
            
            # Safely get profile fields (use getattr with default values)
            profile_photo = getattr(user, 'profile_photo', None)
            bio = getattr(user, 'bio', None)
            interests = getattr(user, 'interests', None)
            
            return {
                "profile": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "profile_photo": profile_photo,
                    "bio": bio,
                    "interests": interests,
                    "created_at": str(user.created_at)
                },
                "activities": {
                    "participated_events": participated_events,
                    "commented_events": commented_events,
                    "liked_events": [],  # Empty for now
                    "disliked_events": [],  # Empty for now
                    "followed_clubs": clubs
                }
            }, 200
            
        except DoesNotExist:
            return {"error": "User not found"}, 404
        except Exception as e:
            print(f"Error in get_user_profile: {str(e)}")
            return {"error": str(e)}, 500

    @staticmethod
    async def update_profile(user_id: int, data: dict):
        """Update user profile information"""
        try:
            user = await Users.get(id=user_id)
            
            # Only update fields that exist in the model
            if "full_name" in data:
                user.full_name = data["full_name"]
            
            # Check if new fields exist before updating
            if hasattr(user, 'profile_photo') and "profile_photo" in data:
                user.profile_photo = data["profile_photo"]
            if hasattr(user, 'bio') and "bio" in data:
                user.bio = data["bio"]
            if hasattr(user, 'interests') and "interests" in data:
                user.interests = data["interests"]
                
            await user.save()
            
            return {
                "message": "Profile updated successfully",
                "profile": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "profile_photo": getattr(user, 'profile_photo', None),
                    "bio": getattr(user, 'bio', None),
                    "interests": getattr(user, 'interests', None)
                }
            }, 200
            
        except DoesNotExist:
            return {"error": "User not found"}, 404
        except Exception as e:
            print(f"Error in update_profile: {str(e)}")
            return {"error": str(e)}, 400