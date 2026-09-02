from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

# Create your tests here.


class OwnerPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="safe-password-123")
        self.owner.profile.role = "owner"
        self.owner.profile.save()
        self.tenant = User.objects.create_user("tenant", password="safe-password-123")

    def test_tenant_cannot_open_add_property_page(self):
        self.client.force_login(self.tenant)
        response = self.client.get(reverse("add_property"))
        self.assertRedirects(response, reverse("home"))

    def test_owner_can_open_add_property_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("add_property"))
        self.assertEqual(response.status_code, 200)
