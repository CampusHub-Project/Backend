from sanic import Blueprint
from sanic.response import json
from src.services.event_service import EventService
from src.middleware import authorized

events_bp = Blueprint("events", url_prefix="/events")

@events_bp.post("/")
@authorized()
async def create_event(request):
    result, status = await EventService.create_event(request.ctx.user, request.json)
    return json(result, status=status)

@events_bp.delete("/<event_id:int>")
@authorized()
async def delete_event(request, event_id):
    result, status = await EventService.delete_event(request.ctx.user, event_id)
    return json(result, status=status)

# --- GÜNCELLENEN ROUTE ---
@events_bp.get("/")
async def list_events(request):
    # Query Parametrelerini Al (?page=1&limit=20&search=xyz)
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        page = 1
        limit = 20
        
    search = request.args.get("search")
    date_filter = request.args.get("date")

    # Servise parametreleri ilet
    result, status = await EventService.get_events(page, limit, search, date_filter)
    return json(result, status=status)

@events_bp.get("/<event_id:int>")
async def get_event_detail(request, event_id):
    result, status = await EventService.get_event_detail(event_id)
    return json(result, status=status)

@events_bp.post("/<event_id:int>/join")
@authorized()
async def join_event(request, event_id):
    result, status = await EventService.join_event(request.ctx.user, event_id)
    return json(result, status=status)

@events_bp.post("/<event_id:int>/leave")
@authorized()
async def leave_event(request, event_id):
    result, status = await EventService.leave_event(request.ctx.user, event_id)
    return json(result, status=status)

@events_bp.post("/<event_id:int>/remove-participant")
@authorized()
async def remove_participant(request, event_id):
    target_user_id = request.json.get("user_id")
    if not target_user_id:
        return json({"error": "User ID is required"}, 400)
    result, status = await EventService.remove_participant(request.ctx.user, event_id, target_user_id)
    return json(result, status=status)