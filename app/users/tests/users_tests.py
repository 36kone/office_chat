from django.test import TestCase
from django.urls import reverse
from app.users.models import User


class UserTestCase(TestCase):

    def test_create_user(self):
        response = self.client.post(
            "/api/users/",
            {
                "name": "Caio",
                "email": "caio@empresa.com",
                "age": 25
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)