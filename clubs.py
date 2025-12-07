from sanic import Blueprint
from sanic.response import json
from database import execute_query, fetch_all
from security import authorized

clubs_bp = Blueprint("clubs", url_prefix="/clubs")

@clubs_bp.post("/")
@authorized()
async def create_club(request):
    user_id = request.ctx.user_id
    data = request.json

    if not data or "club_name" not in data:
        return json({"error": "Kulüp adı zorunludur."}, status=400)

    try:
        club_id = await execute_query(
            """
            INSERT INTO Clubs (club_name, description, logo_url, president_id, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["club_name"],
                data.get("description"),
                data.get("logo_url"),
                user_id, 
                user_id
            )
        )
        return json({"message": "Kulüp oluşturuldu!", "club_id": club_id}, status=201)
    
    except Exception as e:
        return json({"error": f"Bir hata oluştu: {str(e)}"}, status=500)

@clubs_bp.get("/")
async def list_clubs(request):
    clubs = await fetch_all(
        "SELECT club_id, club_name, description, status, logo_url FROM Clubs WHERE is_deleted = FALSE"
    )
    
    return json({"clubs": clubs, "count": len(clubs)})