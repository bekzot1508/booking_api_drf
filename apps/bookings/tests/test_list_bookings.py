from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from apps.resources.models import Resource
from apps.bookings.models import Booking, BookingStatus

User = get_user_model()


class BookingListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@u.com",
            password="StrongPass123",
            full_name="U",
        )

        # token olish
        self.client.post("/auth/register", {"email":"t@t.com","password":"StrongPass123","full_name":"T"}, format="json")
        login = self.client.post("/auth/login", {"email":"t@t.com","password":"StrongPass123"}, format="json")
        self.token = login.data["access_token"]

        self.resource = Resource.objects.create(name="Room A", owner=self.user)

        now = timezone.now()
        self.b1 = Booking.objects.create(
            resource=self.resource,
            user=self.user,
            start_at=now + timedelta(hours=1),
            end_at=now + timedelta(hours=2),
            status=BookingStatus.ACTIVE,
        )
        self.b2 = Booking.objects.create(
            resource=self.resource,
            user=self.user,
            start_at=now + timedelta(days=1, hours=1),
            end_at=now + timedelta(days=1, hours=2),
            status=BookingStatus.CANCELLED,
            cancelled_at=now,
        )

    def test_list_requires_auth(self):
        res = self.client.get("/bookings/")
        self.assertEqual(res.status_code, 401)

    def test_list_all(self):
        res = self.client.get("/bookings/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 2)

    def test_filter_by_status(self):
        res = self.client.get(
            "/bookings/?status=active",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["status"], "active")

    def test_pagination(self):
        res = self.client.get(
            "/bookings/?page=1&page_size=1",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["page_size"], 1)
        self.assertEqual(len(res.data["results"]), 1)

    def test_invalid_status(self):
        res = self.client.get(
            "/bookings/?status=bad",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "VALIDATION_ERROR")
