from sanic import Blueprint
from sanic.response import json
from models import EventComments, Events
from security import authorized

comments_bp = Blueprint("comments", url_prefix="/comments")

@comments_bp.post("/")
@authorized()
async def create_comment(request):
    user_id = request.ctx.user_id
    data = request.json
    
    # 1. Kontrol
    if not data or "event_id" not in data or "comment" not in data:
        return json({"error": "event_id ve comment bilgisi zorunludur."}, status=400)

    # 2. Etkinlik var mı?
    event = await Events.get_or_none(event_id=data["event_id"], is_deleted=False)
    if not event:
        return json({"error": "Etkinlik bulunamadı."}, status=404)

    # 3. Yorumu Kaydet
    try:
        comment = await EventComments.create(
            event_id=data["event_id"],
            user_id=user_id,
            comment=data["comment"]
        )
        return json({"message": "Yorum eklendi!", "comment_id": comment.comment_id}, status=201)
    except Exception as e:
        return json({"error": str(e)}, status=500)

@comments_bp.get("/<event_id:int>")
async def list_comments(request, event_id):
    # O etkinliğe ait, SİLİNMEMİŞ yorumları getir
    # Yorumu yapan kullanıcının adını da getir (select_related)
    comments = await EventComments.filter(
        event_id=event_id, 
        is_deleted=False
    ).select_related("user").values(
        "comment_id",
        "comment",
        "created_at",
        "user__first_name",
        "user__last_name",
        "user__profile_image"
    )
    
    # Tarih formatını düzelt (Datetime Serialization Hatasını önle)
    for c in comments:
        if c["created_at"]:
            c["created_at"] = c["created_at"].isoformat()
            
    return json({"comments": comments, "count": len(comments)})

@comments_bp.delete("/<comment_id:int>")
@authorized()
async def delete_comment(request, comment_id):
    user_id = request.ctx.user_id
    
    # 1. Yorumu bul (Sadece kendi yorumunu silebilir)
    comment = await EventComments.get_or_none(comment_id=comment_id, user_id=user_id)
    
    if not comment:
        return json({"error": "Yorum bulunamadı veya silme yetkiniz yok."}, status=404)
    
    # 2. Soft Delete Uygula
    comment.is_deleted = True
    await comment.save()
    
    return json({"message": "Yorum silindi."})