from sanic import Blueprint
from sanic.response import json
from models import Events, Clubs # <-- Modellerimiz
from security import authorized
from tortoise.exceptions import IntegrityError

events_bp = Blueprint("events", url_prefix="/events")

@events_bp.post("/")
@authorized()
async def create_event(request):
    user_id = request.ctx.user_id
    data = request.json
    
    # 1. Kontroller
    required = ["club_id", "title", "event_date"]
    if not all(k in data for k in required):
        return json({"error": "Eksik bilgi (club_id, title, event_date şart)."}, status=400)

    try:
        # 2. Etkinliği Oluştur (Create)
        event = await Events.create(
            club_id=data["club_id"], # İlişkiyi ID üzerinden kuruyoruz
            title=data["title"],
            description=data.get("description"),
            image_url=data.get("image_url"),
            event_date=data["event_date"], # "YYYY-MM-DD HH:MM:SS" formatında string gönderilmeli
            location=data.get("location"),
            quota=data.get("quota", 0),
            created_by_id=user_id
        )
        return json({"message": "Etkinlik oluşturuldu!", "event_id": event.event_id}, status=201)
    
    except IntegrityError:
        return json({"error": "Veritabanı hatası (Geçersiz Kulüp ID olabilir)."}, status=400)
    except Exception as e:
        return json({"error": str(e)}, status=500)

@events_bp.get("/")
async def list_events(request):
    # --- ORM BÜYÜSÜ BURADA ---
    # 1. .filter(): Sadece silinmemişleri getir.
    # 2. .select_related("club"): SQL'deki JOIN işlemi (Club verilerini de hazırla).
    # 3. .values(): Sadece istediğimiz alanları al.
    #    "club__club_name" -> Club tablosundaki club_name alanını al demektir.
    
    events = await Events.filter(is_deleted=False).select_related("club").values(
        "event_id", 
        "title", 
        "event_date", 
        "location", 
        "image_url",
        "club__club_name", # <--- DİKKAT: İlişkili tablodan veri çekme
        "club__logo_url"
    )
    
    return json({"events": events, "count": len(events)})