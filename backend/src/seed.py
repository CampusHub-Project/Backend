import asyncio
from tortoise import Tortoise
from src.config import DB_URL
from src.models import Users, Clubs, Events, UserRole, ParticipationStatus
from src.security import hash_password

async def seed_data():
    print("🌱 Veritabanı bağlantısı kuruluyor...")
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['src.models']}
    )
    # Şemayı garantiye al
    await Tortoise.generate_schemas()

    print("🗑️  Eski veriler temizleniyor...")
    await Events.all().delete()
    await Clubs.all().delete()
    await Users.all().delete()

    print("👤 Kullanıcılar oluşturuluyor...")
    # 1. Sistem Yöneticisi (Admin)
    admin = await Users.create(
        email="admin@campus.hub",
        password_hash=hash_password("123456"),
        full_name="Sistem Yöneticisi",
        role=UserRole.ADMIN
    )

    # 2. Kulüp Başkanı
    club_admin = await Users.create(
        email="baskan@teknoloji.kulubu",
        password_hash=hash_password("123456"),
        full_name="Tech Başkan",
        role=UserRole.CLUB_ADMIN
    )

    # 3. Öğrenci
    student = await Users.create(
        email="ogrenci@univ.edu",
        password_hash=hash_password("123456"),
        full_name="Ahmet Öğrenci",
        role=UserRole.STUDENT
    )

    print("club 🏰 Kulüpler oluşturuluyor...")
    tech_club = await Clubs.create(
        name="Teknoloji Kulübü",
        description="Yazılım, donanım ve yapay zeka tutkunlarının buluşma noktası.",
        image_url="https://images.unsplash.com/photo-1519389950473-47ba0277781c",
        admin=club_admin
    )

    art_club = await Clubs.create(
        name="Sanat ve Tasarım Kulübü",
        description="Resim, müzik ve dijital sanatlarla ilgilenenler buraya!",
        image_url="https://images.unsplash.com/photo-1513364776144-60967b0f800f",
        admin=admin # Şimdilik admin yönetsin
    )

    print("📅 Etkinlikler oluşturuluyor...")
    await Events.create(
        title="Büyük Hackathon 2024",
        description="48 saat sürecek kodlama maratonuna hazır mısın? Ödüllü yarışma!",
        date="2025-05-20T09:00:00",
        location="Mühendislik Fakültesi - B Blok",
        capacity=100,
        club=tech_club,
        image_url="https://images.unsplash.com/photo-1504384308090-c54be3855833"
    )

    await Events.create(
        title="Python ile Yapay Zeka Atölyesi",
        description="Sıfırdan yapay zeka modelleri eğitmeyi öğreniyoruz.",
        date="2025-06-10T14:00:00",
        location="Online (Zoom)",
        capacity=50,
        club=tech_club,
        image_url="https://images.unsplash.com/photo-1555949963-ff9fe0c870eb"
    )

    await Events.create(
        title="Modern Sanat Sergisi",
        description="Öğrencilerimizin eserlerinden oluşan yıl sonu sergisi.",
        date="2025-04-15T10:00:00",
        location="Kampüs Meydanı",
        capacity=0, # Sınırsız
        club=art_club,
        image_url="https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b"
    )

    print("✅ VERİLER BAŞARIYLA YÜKLENDİ! 🚀")
    print(f"👉 Admin Girişi: admin@campus.hub / 123456")
    print(f"👉 Öğrenci Girişi: ogrenci@univ.edu / 123456")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed_data())