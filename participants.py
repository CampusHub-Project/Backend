from sanic import Blueprint
from sanic.response import json
from models import EventParticipants, Events
from security import authorized
from tortoise.exceptions import IntegrityError

participants_bp = Blueprint("participants", url_prefix="/participants")

@participants_bp.post("/join")
@authorized()
async def join_event(request):
    user_id = request.ctx.user_id
    data = request.json
    
    if not data or "event_id" not in data:
        return json({"error": "Hangi etkinliğe katılacaksın? (event_id eksik)"}, status=400)
    
    event_id = data["event_id"]

    # 1. Etkinlik var mı ve aktif mi?
    event = await Events.get_or_none(event_id=event_id, is_deleted=False)
    if not event:
        return json({"error": "Etkinlik bulunamadı."}, status=404)

    # 2. Kontenjan kontrolü (İleride buraya eklenebilir)

    # 3. Kayıt Ol
    try:
        await EventParticipants.create(
            event_id=event_id,
            user_id=user_id,
            status="going" # Varsayılan: Gidiyor
        )
        return json({"message": "Etkinliğe katıldınız!"}, status=201)

    except IntegrityError:
        return json({"error": "Zaten bu etkinliğe katılımcısısınız."}, status=409)
    except Exception as e:
        return json({"error": str(e)}, status=500)

@participants_bp.delete("/leave")
@authorized()
async def leave_event(request):
    user_id = request.ctx.user_id
    data = request.json
    
    if not data or "event_id" not in data:
        return json({"error": "event_id gerekli"}, status=400)

    # Kaydı silmek yerine 'is_active=False' veya direkt silebiliriz.
    # Şimdilik direkt silelim (Katılımı iptal etme)
    deleted_count = await EventParticipants.filter(
        event_id=data["event_id"], 
        user_id=user_id
    ).delete()

    if deleted_count:
        return json({"message": "Katılım iptal edildi."})
    else:
        return json({"error": "Zaten katılmamışsınız."}, status=404)

@participants_bp.get("/<event_id:int>")
async def list_participants(request, event_id):
    # Bu etkinliğe katılanları listele
    # İlişkili 'user' tablosundan isim ve soyismi çek
    participants = await EventParticipants.filter(
        event_id=event_id, 
        is_active=True
    ).select_related("user").values(
        "status",
        "joined_at",
        "user__first_name",
        "user__last_name",
        "user__profile_image"
    )
    for p in participants:
        if p["joined_at"]:
            # isoformat(), tarihi "2025-12-11T15:30:00" gibi standart bir metne çevirir
            p["joined_at"] = p["joined_at"].isoformat()
            
    return json({"participants": participants, "count": len(participants)})