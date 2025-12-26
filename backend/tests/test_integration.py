import pytest
import pytest_asyncio
from tortoise import Tortoise
from src.models import Users, UserRole, Clubs, ClubFollowers, Events, EventParticipation, ParticipationStatus
from src.security import hash_password
from src.config import TORTOISE_ORM
from datetime import datetime, timedelta

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)
    yield
    await Tortoise.close_connections()

@pytest.mark.asyncio
async def test_club_follower_workflow():
    """Kulüp oluşturma ve takipçi ekleme akışını test eder."""
    # last_name alanlarını ekledik!
    admin = await Users.create(
        user_id=888, email="admin_test@campus.hub", 
        password=hash_password("123"), first_name="Admin", last_name="Test", role=UserRole.ADMIN
    )
    student = await Users.create(
        user_id=777, email="student_test@campus.hub", 
        password=hash_password("123"), first_name="Ogrenci", last_name="Soyad", role=UserRole.STUDENT
    )

    club = await Clubs.create(
        club_name="Test Teknoloji Kulübü",
        description="Entegrasyon testi için",
        president=admin,
        status="active"
    )

    follower_rel = await ClubFollowers.create(user=student, club=club)
    exists = await ClubFollowers.filter(user_id=777, club_id=club.club_id).exists()
    assert exists is True
    
    await follower_rel.delete()
    await club.delete()
    await admin.delete()
    await student.delete()

@pytest.mark.asyncio
async def test_event_participation_integration():
    """Etkinlik oluşturma ve katılım sürecini test eder."""
    user = await Users.create(
        user_id=666, email="event_test@campus.hub", 
        password=hash_password("123"), first_name="Katilimci", last_name="Deneme"
    )
    # Kulüp için bir başkan gerekebilir, modeline göre boş geçtik ama hata verirse başkan ekleriz
    club = await Clubs.create(club_name="Etkinlik Kulübü", status="active")

    event = await Events.create(
        title="Büyük Hackathon",
        event_date=datetime.now() + timedelta(days=5),
        club=club,
        quota=100
    )

    participation = await EventParticipation.create(
        user=user,
        event=event,
        status=ParticipationStatus.GOING
    )

    p_data = await EventParticipation.get(event_id=event.event_id).prefetch_related("user")
    assert p_data.user.user_id == 666

    await participation.delete()
    await event.delete()
    await club.delete()
    await user.delete()