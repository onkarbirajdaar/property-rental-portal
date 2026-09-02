from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.


class RegistrationTests(TestCase):
    def test_registration_saves_selected_role(self):
        response = self.client.post(reverse("register"), {
            "username": "new-owner",
            "role": "owner",
            "password1": "Strong-password-123",
            "password2": "Strong-password-123",
        })

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(User.objects.get(username="new-owner").profile.role, "owner")
