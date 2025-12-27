from src.models import EventComments, Events, Users
from tortoise.exceptions import DoesNotExist

class CommentService:

    @staticmethod
    async def add_comment(user_ctx, event_id: int, content: str):
        if not await Events.exists(event_id=event_id):
            return {"error": "Event not found"}, 404

        comment = await EventComments.create(
            user_id=user_ctx["sub"],
            event_id=event_id,
            content=content
        )
        return {"message": "Comment added", "id": comment.comment_id}, 201

    @staticmethod
    async def get_comments(event_id: int):
        comments = await EventComments.filter(event_id=event_id).prefetch_related("user").order_by("-created_at")
        
        result = []
        for c in comments:
            full_name = "Unknown User"
            if c.user:
                full_name = f"{c.user.first_name} {c.user.last_name}"

            result.append({
                "id": c.comment_id,
                "content": c.content,
                "user_name": full_name,
                "created_at": str(c.created_at)
            })
        return {"comments": result}, 200