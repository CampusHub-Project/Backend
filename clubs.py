from sanic import Blueprint
from sanic.response import json
from models import Clubs # <-- Model
from security import authorized
from tortoise.exceptions import IntegrityError

clubs_bp = Blueprint("clubs", url_prefix="/clubs")

@clubs_bp.post("/")
@authorized()
async def create_club(request):
    user_id = request.ctx.user_id
    data = request.json

    if not data or "club_name" not in data:
        return json({"error": "Kulüp adı zorunludur."}, status=400)

    try:
        club = await Clubs.create(
            club_name=data["club_name"],
            description=data.get("description"),
            logo_url=data.get("logo_url"),
            president_id=user_id, 
            created_by_id=user_id
        )
        return json({"message": "Kulüp oluşturuldu!", "club_id": club.club_id}, status=201)
    
    except IntegrityError:
        return json({"error": "Bu isimde bir kulüp zaten var."}, status=400)
    except Exception as e:
        return json({"error": str(e)}, status=500)

@clubs_bp.get("/")
async def list_clubs(request):

    clubs = await Clubs.filter(is_deleted=False).values(
        "club_id", "club_name", "description", "status", "logo_url"
    )
    
    return json({"clubs": clubs, "count": len(clubs)})