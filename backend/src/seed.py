import asyncio
from tortoise import Tortoise
from src.config import DB_URL
from src.models import Users, Clubs, Events, UserRole
from src.security import hash_password

async def seed_data():
    print("🌱 Veritabanı bağlantısı kuruluyor...")
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['src.models']}
    )
    # Şemayı oluştur (Eski tabloları silip yenisini kurar)
    await Tortoise.generate_schemas()

    print("🗑️  Tablolar temizleniyor...")
    await Events.all().delete()
    await Clubs.all().delete()
    await Users.all().delete()

    print("👤 Kullanıcılar (Öğrenci No ile) oluşturuluyor...")
    
    # 1. Sistem Yöneticisi (ID: 1000)
    admin = await Users.create(
        user_id=1000, 
        email="admin@campus.hub",
        password=hash_password("123456"),
        first_name="Sistem",
        last_name="Yöneticisi",
        role=UserRole.ADMIN,
        department="Bilgi İşlem"
    )

    # 2. Kulüp Başkanı (ID: 20201001)
    club_admin = await Users.create(
        user_id=20201001, 
        email="baskan@teknoloji.kulubu",
        password=hash_password("123456"),
        first_name="Can",
        last_name="Tekno",
        role=UserRole.CLUB_ADMIN,
        department="Bilgisayar Mühendisliği"
    )

    # 3. Öğrenci (ID: 20232005)
    student = await Users.create(
        user_id=20232005, 
        email="ogrenci@univ.edu",
        password=hash_password("123456"),
        first_name="Ahmet",
        last_name="Çalışkan",
        role=UserRole.STUDENT,
        department="Endüstri Mühendisliği"
    )

    print("🏰 Kulüpler oluşturuluyor...")
    tech_club = await Clubs.create(
        club_name="Teknoloji Kulübü",
        description="Yazılım, donanım ve yapay zeka tutkunlarının buluşma noktası.",
        logo_url="https://images.unsplash.com/photo-1519389950473-47ba0277781c",
        president=club_admin,
        created_by=admin
    )

    art_club = await Clubs.create(
        club_name="Sanat ve Tasarım Kulübü",
        description="Resim, müzik ve dijital sanatlarla ilgilenenler buraya!",
        logo_url="https://images.unsplash.com/photo-1513364776144-60967b0f800f",
        president=admin,
        created_by=admin
    )

    print("📅 Etkinlikler oluşturuluyor...")
    await Events.create(
        title="Büyük Hackathon 2024",
        description="48 saat sürecek kodlama maratonuna hazır mısın?",
        event_date="2025-05-20T09:00:00",
        location="Mühendislik Fakültesi - B Blok",
        quota=100,
        club=tech_club,
        image_url="https://images.unsplash.com/photo-1504384308090-c54be3855833",
        created_by=club_admin
    )

    print("✅ VERİLER BAŞARIYLA YÜKLENDİ! 🚀")
    print(f"👉 Admin: admin@campus.hub (Pass: 123456)")
    print(f"👉 Kulüp Başkanı: baskan@teknoloji.kulubu")
    print(f"👉 Öğrenci: ogrenci@univ.edu")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed_data())