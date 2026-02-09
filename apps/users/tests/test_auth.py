from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_success(self):
        res = self.client.post(
            "/auth/register",
            {"email": "bekzod@mail.com", "password": "StrongPass123", "full_name": "Bekzod Ali"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)

    def test_register_with_existing_email_fails(self):
        payload = {
            "email": "bekzod@mail.com",
            "password": "StrongPass123",
            "full_name": "Bekzod Ali",
        }

        # birinchi marta — OK
        res1 = self.client.post("/auth/register", payload, format="json")
        self.assertEqual(res1.status_code, 201)

        # ikkinchi marta — ERROR bo‘lishi kerak
        res2 = self.client.post("/auth/register", payload, format="json")
        self.assertEqual(res2.status_code, 400)

        self.assertEqual(res2.data["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(
            res2.data["error"]["message"],
            "Email already registered"
        )
        self.assertEqual(
            res2.data["error"]["details"]["email"],
            "bekzod@mail.com"
        )

    def test_login_success(self):
        self.client.post(
            "/auth/register",
            {"email": "bekzod@mail.com", "password": "StrongPass123", "full_name": "Bekzod Ali"},
            format="json",
        )
        res = self.client.post(
            "/auth/login",
            {"email": "bekzod@mail.com", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access_token", res.data)

    def test_login_wrong_password(self):
        self.client.post(
            "/auth/register",
            {"email": "bekzod@mail.com", "password": "StrongPass123", "full_name": "Bekzod Ali"},
            format="json",
        )
        res = self.client.post(
            "/auth/login",
            {"email": "bekzod@mail.com", "password": "WrongPass123"},
            format="json",
        )
        self.assertEqual(res.status_code, 401)
