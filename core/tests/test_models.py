import pytest
from django.utils import timezone
from core.models import User, Event, Category

@pytest.mark.django_db
def test_event_creation():
    user = User.objects.create_user(email="test@example.com", password="testpass123")
    event = Event.objects.create(
        user=user,
        name="Test Event",
        description="This is a test event",
        shortcode="EVT123",
        amount_per_vote=1.5,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(days=1)
    )
    
    assert event.shortcode == "EVT123"
    assert event.user == user

@pytest.mark.django_db
def test_category_linked_to_event():
    user = User.objects.create_user(email="cat@test.com", password="pass")
    event = Event.objects.create(
        user=user, name="Test", description="", shortcode="CATE01",
        amount_per_vote=2, start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(days=1)
    )
    category = Category.objects.create(event=event, name="Most Creative")
    assert category in event.categories.all()
