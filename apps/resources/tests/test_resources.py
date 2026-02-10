from rest_framework.test import APITestCase


class ResourceTests(APITestCase):
    def _register_and_login(self):
        self.client.post("/auth/register", {"email":"a@a.com","password":"StrongPass123","full_name":"A"}, format="json")
        r = self.client.post("/auth/login", {"email":"a@a.com","password":"StrongPass123"}, format="json")
        return r.data["access_token"]

    def test_create_resource_requires_auth(self):
        res = self.client.post("/resources/", {"name": "Room A"}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_create_resource_success(self):
        token = self._register_and_login()
        res = self.client.post(
            "/resources/",
            {"name": "Room A"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["name"], "Room A")
