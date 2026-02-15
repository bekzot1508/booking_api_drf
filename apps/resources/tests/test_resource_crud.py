from rest_framework.test import APITestCase


class ResourceCRUDTests(APITestCase):
    def _register_login(self, email):
        self.client.post("/auth/register", {"email": email, "password": "StrongPass123", "full_name": "X"}, format="json")
        r = self.client.post("/auth/login", {"email": email, "password": "StrongPass123"}, format="json")
        return r.data["access_token"]

    def test_crud_flow_owner(self):
        token = self._register_login("owner@a.com")

        # create
        res = self.client.post("/resources/", {"name": "Room A"}, format="json", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 201)
        rid = res.data["id"]

        # list
        res = self.client.get("/resources/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)

        # retrieve
        res = self.client.get(f"/resources/{rid}/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)

        # update
        res = self.client.patch(f"/resources/{rid}/", {"name": "Room A2"}, format="json", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "Room A2")

        # delete
        res = self.client.delete(f"/resources/{rid}/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 204)
