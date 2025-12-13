from sanic import Blueprint
from sanic.response import json
from src.services.event_service import EventService
from src.middleware import authorized

events_bp = Blueprint("events", url_prefix="/events")

@events_bp.post("/")
@authorized()
async def create_event(request):
    # Etkinlik oluştur
    result, status = await EventService.create_event(request.ctx.user, request.json)
    return json(result, status=status)

@events_bp.get("/")
async def list_events(request):
    # Etkinlikleri listele
    result, status = await EventService.get_events()
    return json(result, status=status)

@events_bp.get("/<event_id:int>")
async def get_event_detail(request, event_id):
    # Etkinlik detayını getir
    result, status = await EventService.get_event_detail(event_id)
    return json(result, status=status)

@events_bp.post("/<event_id:int>/join")
@authorized()
async def join_event(request, event_id):
    # Etkinliğe katıl
    result, status = await EventService.join_event(request.ctx.user, event_id)
    return json(result, status=status)