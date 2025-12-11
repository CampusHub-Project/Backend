from sanic import Blueprint
from sanic.response import json
from models import Notifications
from security import authorized

notifications_bp = Blueprint("notifications", url_prefix="/notifications")

@notifications_bp.get("/")
@authorized()
async def list_notifications(request):
    user_id = request.ctx.user_id
    
    notifs = await Notifications.filter(user_id=user_id).order_by("-is_read", "-created_at").values(
        "notification_id",
        "message",
        "is_read",
        "created_at",
        "club__club_name", 
        "event__title"     
    )
    
    for n in notifs:
        if n["created_at"]:
            n["created_at"] = n["created_at"].isoformat()
            
    return json({"notifications": notifs})

@notifications_bp.put("/<notification_id:int>/read")
@authorized()
async def mark_as_read(request, notification_id):
    user_id = request.ctx.user_id
    
    notif = await Notifications.get_or_none(notification_id=notification_id, user_id=user_id)
    
    if not notif:
        return json({"error": "Bildirim bulunamadı."}, status=404)
        
    notif.is_read = True
    await notif.save()
    
    return json({"message": "Okundu olarak işaretlendi."})