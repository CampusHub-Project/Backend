from src.models import EventComments, Events, Users
from tortoise.exceptions import DoesNotExist

class CommentService:

    @staticmethod
    async def add_comment(user_ctx, event_id: int, content: str):
        # Etkinlik var mı? (Yeni modelde primary key: event_id)
        if not await Events.exists(event_id=event_id):
            return {"error": "Event not found"}, 404

        # Yorum oluştur (user_id manuel değil, token'dan gelen ID kullanılır)
        # Not: Tortoise ORM FK alanları için user_id=... şeklinde argüman kabul eder.
        comment = await EventComments.create(
            user_id=user_ctx["sub"],
            event_id=event_id,
            content=content
        )
        return {"message": "Comment added", "id": comment.comment_id}, 201

    @staticmethod
    async def get_comments(event_id: int):
        # Yorumları ve yazan kullanıcıyı getir
        # prefetch_related("user") sayesinde user tablosuna join atılır
        comments = await EventComments.filter(event_id=event_id).prefetch_related("user").order_by("-created_at")
        
        result = []
        for c in comments:
            # Kullanıcı adı ve soyadını birleştir (Eski modelde full_name vardı)
            full_name = "Unknown User"
            if c.user:
                full_name = f"{c.user.first_name} {c.user.last_name}"

            result.append({
                "id": c.comment_id, # Yeni PK: comment_id
                "content": c.content,
                "user_name": full_name, # Frontend bu formatı bekliyor
                "created_at": str(c.created_at)
            })
        return {"comments": result}, 200