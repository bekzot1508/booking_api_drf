from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.resources.models import Resource
from apps.bookings.models import Booking, BookingStatus

User = get_user_model()


class BookingCancelTests(APITestCase):
    def _register_login(self, email):
        self.client.post("/auth/register", {"email": email, "password": "StrongPass123", "full_name": "X"}, format="json")
        login = self.client.post("/auth/login", {"email": email, "password": "StrongPass123"}, format="json")
        return login.data["access_token"]

    def setUp(self):
        # owner token
        self.owner_token = self._register_login("owner@a.com")
        self.owner = User.objects.get(email="owner@a.com")

        # other token
        self.other_token = self._register_login("other@a.com")
        self.other = User.objects.get(email="other@a.com")

        self.resource = Resource.objects.create(name="Room A", owner=self.owner)

        start = timezone.now() + timedelta(days=1, hours=1)
        end = start + timedelta(hours=1)

        self.booking = Booking.objects.create(
            resource=self.resource,
            user=self.owner,
            start_at=start,
            end_at=end,
            status=BookingStatus.ACTIVE,
        )

    def test_cancel_by_owner_success(self):
        res = self.client.patch(
            f"/bookings/{self.booking.id}/cancel",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.owner_token}",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "cancelled")

    def test_cancel_by_other_forbidden(self):
        res = self.client.patch(
            f"/bookings/{self.booking.id}/cancel",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.other_token}",
        )
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data["error"]["code"], "FORBIDDEN")

    def test_cancel_twice_fails(self):
        # first cancel
        self.client.patch(
            f"/bookings/{self.booking.id}/cancel",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.owner_token}",
        )
        # second cancel should fail
        res2 = self.client.patch(
            f"/bookings/{self.booking.id}/cancel",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.owner_token}",
        )
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.data["error"]["code"], "BUSINESS_RULE_VIOLATION")

    def test_cancel_by_admin_success(self):
        # make other user admin
        self.other.is_staff = True
        self.other.save(update_fields=["is_staff"])

        res = self.client.patch(
            f"/bookings/{self.booking.id}/cancel",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.other_token}",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "cancelled")
