import asyncio
from tortoise import Tortoise
from src.config import DB_URL
from src.models import Users, Clubs, Events, UserRole
from src.security import hash_password
from datetime import datetime, timedelta

async def seed_data():
    print("🌱 Veritabanı bağlantısı kuruluyor...")
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['src.models']}
    )
    await Tortoise.generate_schemas()

    print("🗑️  Tablolar temizleniyor...")
    await Events.all().delete()
    await Clubs.all().delete()
    await Users.all().delete()

    print("👤 Kullanıcılar oluşturuluyor...")
    
    # 1. Admin (ID: 1000)
    admin = await Users.create(
        user_id=1000, 
        email="admin@campus.hub",
        password=hash_password("123456"),
        first_name="Sistem",
        last_name="Yöneticisi",
        role=UserRole.ADMIN,
        department="IT"
    )

    # 2. Kulüp Başkanı (ID: 2001)
    president = await Users.create(
        user_id=2001, 
        email="baskan@teknoloji.kulubu",
        password=hash_password("123456"),
        first_name="Can",
        last_name="Tekno",
        role=UserRole.CLUB_ADMIN,
        department="Bilgisayar Müh."
    )

    # 3. Öğrenci (ID: 3001)
    student = await Users.create(
        user_id=3001, 
        email="ogrenci@univ.edu",
        password=hash_password("123456"),
        first_name="Ali",
        last_name="Öğrenci",
        role=UserRole.STUDENT,
        department="Endüstri Müh."
    )

    print("🏰 Kulüpler oluşturuluyor...")
    
    # Aktif Kulüp
    tech_club = await Clubs.create(
        club_name="Teknoloji Kulübü",
        description="Yazılım ve Donanım.",
        logo_url="https://via.placeholder.com/150",
        president=president,
        created_by=admin,
        status="active"
    )

    # Onay Bekleyen Kulüp (Test için)
    chess_club = await Clubs.create(
        club_name="Satranç Kulübü",
        description="Zeka oyunları.",
        logo_url="https://via.placeholder.com/150",
        president=student, # Öğrenci başvurdu varsayalım
        created_by=student,
        status="pending"
    )

    print("📅 Etkinlikler oluşturuluyor (Pagination Testi İçin)...")
    
    # 1. Büyük Hackathon (Arama testi için spesifik isim)
    await Events.create(
        title="Büyük Hackathon 2025",
        description="48 saatlik kodlama maratonu.",
        event_date=datetime.now() + timedelta(days=30),
        location="Ana Kampüs",
        quota=100,
        club=tech_club,
        created_by=president
    )

    # 2. Python Workshop (Arama testi için)
    await Events.create(
        title="Python ile Veri Analizi",
        description="Pandas ve NumPy eğitimi.",
        event_date=datetime.now() + timedelta(days=10),
        location="Online",
        quota=50,
        club=tech_club,
        created_by=president
    )

    # 3. Pagination testi için 25 adet döngüsel etkinlik
    for i in range(1, 26):
        await Events.create(
            title=f"Haftalık Toplantı #{i}",
            description=f"Teknoloji kulübü haftalık olağan toplantısı {i}.",
            event_date=datetime.now() + timedelta(days=i),
            location="B-Blok Z06",
            quota=20,
            club=tech_club,
            created_by=president
        )

    print("✅ VERİLER YÜKLENDİ!")
    print(f"👉 Admin: admin@campus.hub (123456)")
    print(f"👉 Öğrenci: ogrenci@univ.edu (123456)")
    print(f"👉 Onaylanacak Kulüp ID: {chess_club.club_id} (Satranç)")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed_data())