from src.models import Users, Clubs, Events, UserRole, EventComments, Notifications
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q # <--- Arama için Q nesnesini ekledik
from tortoise.transactions import in_transaction # <-- BU IMPORT EKLENMELİ
from src.config import logger

class AdminService:

    @staticmethod
    async def get_dashboard_stats():
        """Admin paneli ana sayfası için özet veriler"""
        try:
            total_users = await Users.filter(is_deleted=False).count()
            total_clubs = await Clubs.filter(is_deleted=False, status="active").count()
            pending_clubs = await Clubs.filter(status="pending").count()
            total_events = await Events.filter(is_deleted=False).count()

            return {
                "stats": {
                    "users": total_users,
                    "active_clubs": total_clubs,
                    "pending_clubs": pending_clubs,
                    "events": total_events
                }
            }, 200
        except Exception as e:
            logger.error(f"Stats Error: {str(e)}")
            return {"error": "Failed to fetch stats"}, 500

    @staticmethod
    async def get_all_users(page: int, limit: int, search: str = None):
        """Kullanıcıları listeleme ve arama"""
        query = Users.all()

        if search:
            # Hem İsim, Hem Soyisim hem de Email içinde arama yap (Q ile OR mantığı)
            query = query.filter(
                Q(email__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search)
            )

        total = await query.count()
        # En son kayıt olanlar en üstte görünsün (-created_at)
        users = await query.offset((page - 1) * limit).limit(limit).order_by("-created_at")

        users_list = [{
            "id": u.user_id,
            "full_name": f"{u.first_name} {u.last_name}",
            "email": u.email,
            "role": u.role,
            "department": u.department,
            "is_active": not u.is_deleted
        } for u in users]

        return {
            "users": users_list,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }, 200

    @staticmethod
    async def toggle_user_ban(target_user_id: int):
        """Kullanıcıyı yasakla / yasağını kaldır"""
        try:
            user = await Users.get(user_id=target_user_id)
            if user.role == UserRole.ADMIN:
                return {"error": "Cannot ban an admin"}, 400
            
            # Durumu tersine çevir
            user.is_deleted = not user.is_deleted
            await user.save()
            
            action = "Banned" if user.is_deleted else "Unbanned"
            logger.info(f"User {target_user_id} was {action} by admin.")
            
            return {"message": f"User {action} successfully", "is_active": not user.is_deleted}, 200
        except DoesNotExist:
            return {"error": "User not found"}, 404

    @staticmethod
    async def delete_comment(comment_id: int):
        """A. Yorum Denetimi: İstenmeyen yorumu sil"""
        deleted_count = await EventComments.filter(comment_id=comment_id).delete()
        if deleted_count == 0:
            return {"error": "Comment not found"}, 404
        
        logger.info(f"Comment {comment_id} deleted by admin.")
        return {"message": "Comment deleted successfully"}, 200

    @staticmethod
    async def update_user_role(user_id: int, new_role: str):
        """B. Rol Yönetimi: Kullanıcı yetkisini değiştir"""
        # Gelen rol string'i Enum içinde var mı kontrol et
        if new_role not in [r.value for r in UserRole]:
            return {"error": f"Invalid role. Valid options: {[r.value for r in UserRole]}"}, 400
            
        try:
            user = await Users.get(user_id=user_id)
            old_role = user.role
            user.role = UserRole(new_role)
            await user.save()
            
            logger.info(f"Role Change: User {user_id} changed from {old_role} to {new_role} by admin.")
            return {"message": f"User role updated to {new_role}"}, 200
        except DoesNotExist:
            return {"error": "User not found"}, 404

    @staticmethod
    async def send_global_announcement(message: str):
        """C. Sistem Duyurusu: Herkese bildirim gönder"""
        if not message:
            return {"error": "Message content is required"}, 400

        try:
            # Tüm aktif kullanıcıların ID'lerini al
            users = await Users.filter(is_deleted=False).all()
            
            # Toplu insert işlemi (Tek tek create yapmaktan çok daha hızlıdır)
            notif_objects = [
                Notifications(user_id=u.user_id, message=f"📢 SİSTEM DUYURUSU: {message}") 
                for u in users
            ]
            
            await Notifications.bulk_create(notif_objects)
            
            logger.info(f"Global Announcement Sent to {len(users)} users: {message}")
            return {"message": f"Announcement sent to {len(users)} users"}, 200
        except Exception as e:
            logger.error(f"Announcement Error: {str(e)}")
            return {"error": "Failed to send announcement"}, 500

    @staticmethod
    async def update_club_details(club_id: int, data: dict):
        """D. Kulüp İçerik Müdahalesi + Otomatik Başkan Rol Yönetimi"""
        try:
            # Transaction (Atomik İşlem) başlatıyoruz. Hata olursa her şeyi geri alır.
            async with in_transaction():
                club = await Clubs.get(club_id=club_id)
                
                changes = []
                
                # 1. Standart Bilgileri Güncelle
                if "name" in data:
                    club.club_name = data["name"]
                    changes.append("name")
                if "description" in data:
                    club.description = data["description"]
                    changes.append("description")
                if "image_url" in data:
                    club.logo_url = data["image_url"]
                    changes.append("image")
                
                # 2. BAŞKAN DEĞİŞİKLİĞİ VAR MI? (Otomatik Rol Yönetimi)
                if "president_id" in data:
                    new_pid = int(data["president_id"])
                    
                    # Eğer başkan zaten aynıysa işlem yapma
                    if club.president_id != new_pid:
                        
                        # A. Yeni Başkan Adayını Bul
                        new_president = await Users.get_or_none(user_id=new_pid)
                        if not new_president:
                            return {"error": "New president user not found"}, 404
                            
                        # B. Eski Başkanı Bul ve Yetkisini Düşür (Eğer Admin Değilse)
                        if club.president_id:
                            old_president = await Users.get_or_none(user_id=club.president_id)
                            # Eski başkan varsa ve rolü 'club_admin' ise -> 'student' yap
                            # (Admin ise dokunma, sistem admini kulüp başkanı olmuş olabilir)
                            if old_president and old_president.role == UserRole.CLUB_ADMIN:
                                old_president.role = UserRole.STUDENT
                                await old_president.save()
                                logger.info(f"Auto-Downgrade: User {old_president.user_id} role changed to STUDENT")

                        # C. Yeni Başkanı Yükselt (Eğer Admin Değilse)
                        if new_president.role == UserRole.STUDENT:
                            new_president.role = UserRole.CLUB_ADMIN
                            await new_president.save()
                            logger.info(f"Auto-Upgrade: User {new_president.user_id} role changed to CLUB_ADMIN")
                        
                        # D. Kulüp Kaydını Güncelle
                        club.president_id = new_pid
                        changes.append(f"president_id (changed from {club.president_id} to {new_pid})")

                # Eğer hiçbir değişiklik yoksa
                if not changes:
                    return {"message": "No changes detected"}, 200

                await club.save()
                logger.info(f"Club {club_id} updated by Admin. Fields: {changes}")
                
                return {"message": "Club updated successfully", "club": {
                    "id": club.club_id,
                    "name": club.club_name,
                    "president_id": club.president_id
                }}, 200

        except DoesNotExist:
            return {"error": "Club not found"}, 404
        except Exception as e:
            logger.error(f"Update Club Error: {str(e)}")
            return {"error": str(e)}, 500