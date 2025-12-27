from sanic import Blueprint
from sanic.response import json
from src.services.admin_service import AdminService
from src.middleware import authorized, admin_only

admin_bp = Blueprint("admin", url_prefix="/admin")

@admin_bp.get("/stats")
@authorized()
@admin_only()
async def get_stats(request):
    result, status = await AdminService.get_dashboard_stats()
    return json(result, status=status)

@admin_bp.get("/users")
@authorized()
@admin_only()
async def list_users(request):
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        search = request.args.get("search")
    except ValueError:
        page = 1
        limit = 20
        search = None
    result, status = await AdminService.get_all_users(page, limit, search)
    return json(result, status=status)

@admin_bp.post("/users/<user_id:int>/ban")
@authorized()
@admin_only()
async def ban_user(request, user_id):
    result, status = await AdminService.toggle_user_ban(user_id)
    return json(result, status=status)


@admin_bp.delete("/comments/<comment_id:int>")
@authorized()
@admin_only()
async def delete_comment(request, comment_id):
    result, status = await AdminService.delete_comment(comment_id)
    return json(result, status=status)

@admin_bp.patch("/users/<user_id:int>/role")
@authorized()
@admin_only()
async def update_role(request, user_id):
    new_role = request.json.get("role")
    if not new_role:
        return json({"error": "Role is required"}, 400)
    result, status = await AdminService.update_user_role(user_id, new_role)
    return json(result, status=status)

@admin_bp.post("/announce")
@authorized()
@admin_only()
async def make_announcement(request):
    message = request.json.get("message")
    result, status = await AdminService.send_global_announcement(message)
    return json(result, status=status)

@admin_bp.put("/clubs/<club_id:int>")
@authorized()
@admin_only()
async def update_club(request, club_id):
    result, status = await AdminService.update_club_details(club_id, request.json)
    return json(result, status=status)