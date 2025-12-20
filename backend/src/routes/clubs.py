from sanic import Blueprint
from sanic.response import json
from src.services.club_service import ClubService
from src.middleware import authorized

clubs_bp = Blueprint("clubs", url_prefix="/clubs")

@clubs_bp.post("/")
@authorized()
async def create_club(request):
    result, status = await ClubService.create_club(request.ctx.user, request.json)
    return json(result, status=status)

@clubs_bp.post("/<club_id:int>/approve")
@authorized()
async def approve_club(request, club_id):
    result, status = await ClubService.approve_club(request.ctx.user, club_id)
    return json(result, status=status)

@clubs_bp.delete("/<club_id:int>")
@authorized()
async def delete_club(request, club_id):
    result, status = await ClubService.delete_club(request.ctx.user, club_id)
    return json(result, status=status)

# --- GÜNCELLENEN ROUTE (REDIS EKLENDİ) ---
@clubs_bp.get("/")
async def list_clubs(request):
    redis = request.app.ctx.redis
    result, status = await ClubService.get_all_clubs(redis)
    return json(result, status=status)

@clubs_bp.get("/<club_id:int>")
async def get_club(request, club_id):
    result, status = await ClubService.get_club_details(club_id)
    return json(result, status=status)

@clubs_bp.post("/<club_id:int>/follow")
@authorized()
async def follow_club(request, club_id):
    result, status = await ClubService.follow_club(request.ctx.user, club_id)
    return json(result, status=status)

@clubs_bp.post("/<club_id:int>/leave")
@authorized()
async def leave_club(request, club_id):
    result, status = await ClubService.leave_club(request.ctx.user, club_id)
    return json(result, status=status)

@clubs_bp.post("/<club_id:int>/remove-member")
@authorized()
async def remove_member(request, club_id):
    target_user_id = request.json.get("user_id")
    if not target_user_id:
        return json({"error": "User ID is required"}, 400)
    result, status = await ClubService.remove_follower(request.ctx.user, club_id, target_user_id)
    return json(result, status=status)

@clubs_bp.get("/my-clubs")
@authorized()
async def get_my_clubs(request):
    result, status = await ClubService.get_my_clubs(request.ctx.user)
    return json(result, status=status)