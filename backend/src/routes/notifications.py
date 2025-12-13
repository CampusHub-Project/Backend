from sanic import Blueprint
from sanic.response import json
from src.services.notification_service import NotificationService
from src.middleware import authorized

notif_bp = Blueprint("notifications", url_prefix="/notifications")

@notif_bp.get("/")
@authorized()
async def get_notifications(request):
    user_id = request.ctx.user["sub"]
    result, status = await NotificationService.get_my_notifications(user_id)
    return json(result, status=status)

@notif_bp.post("/<notif_id:int>/read")
@authorized()
async def mark_read(request, notif_id):
    user_id = request.ctx.user["sub"]
    result, status = await NotificationService.mark_as_read(notif_id, user_id)
    return json(result, status=status)