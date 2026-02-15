from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.resources.models import Resource
from apps.bookings.models import Booking, BookingStatus

User = get_user_model()


class BookingCreateTests(APITestCase):
    def setUp(self):
        # user + token
        self.client.post("/auth/register", {"email":"a@a.com","password":"StrongPass123","full_name":"A"}, format="json")
        login = self.client.post("/auth/login", {"email":"a@a.com","password":"StrongPass123"}, format="json")
        self.token = login.data["access_token"]

        self.user = User.objects.get(email="a@a.com")
        self.resource = Resource.objects.create(name="Room A", owner=self.user)

    def test_create_booking_success(self):
        start = timezone.now() + timedelta(days=1, hours=1)
        end = start + timedelta(hours=1)

        res = self.client.post(
            "/bookings/",
            {"resource_id": str(self.resource.id), "start_at": start.isoformat(), "end_at": end.isoformat()},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["status"], "active")
        self.assertEqual(res.data["resource_id"], str(self.resource.id))

    def test_create_booking_overlap_fails(self):
        start = timezone.now() + timedelta(days=1, hours=1)
        end = start + timedelta(hours=1)

        Booking.objects.create(
            resource=self.resource,
            user=self.user,
            start_at=start,
            end_at=end,
            status=BookingStatus.ACTIVE,
        )

        # overlap interval
        res = self.client.post(
            "/bookings/",
            {"resource_id": str(self.resource.id),
             "start_at": (start + timedelta(minutes=30)).isoformat(),
             "end_at": (end + timedelta(minutes=30)).isoformat()},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "BUSINESS_RULE_VIOLATION")

    def test_create_booking_invalid_time_fails(self):
        start = timezone.now() + timedelta(days=1)
        end = start  # equal

        res = self.client.post(
            "/bookings/",
            {"resource_id": str(self.resource.id), "start_at": start.isoformat(), "end_at": end.isoformat()},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "VALIDATION_ERROR")

    def test_create_booking_min_duration_fails(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=10)  # < 15

        res = self.client.post(
            "/bookings/",
            {"resource_id": str(self.resource.id), "start_at": start.isoformat(), "end_at": end.isoformat()},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "VALIDATION_ERROR")
