from sanic import Blueprint
from sanic.response import json
from src.services.comment_service import CommentService
from src.middleware import authorized

# URL yapısı: /events/<id>/comments şeklinde olacak
comments_bp = Blueprint("comments", url_prefix="/events")

@comments_bp.post("/<event_id:int>/comments")
@authorized()
async def add_comment(request, event_id):
    content = request.json.get("content")
    if not content:
        return json({"error": "Content is required"}, 400)
        
    result, status = await CommentService.add_comment(request.ctx.user, event_id, content)
    return json(result, status=status)

@comments_bp.get("/<event_id:int>/comments")
async def get_comments(request, event_id):
    result, status = await CommentService.get_comments(event_id)
    return json(result, status=status)