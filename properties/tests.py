from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

from .models import Interest, Property, Wishlist

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


class TenantActionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="safe-password-123")
        self.owner.profile.role = "owner"
        self.owner.profile.save()
        self.tenant = User.objects.create_user("tenant", password="safe-password-123")
        self.property = Property.objects.create(
            owner=self.owner,
            title="Sunny apartment",
            property_type="Apartment",
            rent=Decimal("15000.00"),
            deposit=Decimal("30000.00"),
            bhk=2,
            furnished="Furnished",
            address="1 Main Street",
            city="Pune",
            area="Kothrud",
            description="A bright home",
            contact_number="9876543210",
            image="properties/test.jpg",
        )

    def test_anonymous_interest_post_redirects_to_login(self):
        response = self.client.post(
            reverse("property_detail", args=[self.property.id]),
            {"message": "I am interested."},
        )
        expected_url = f"{reverse('login')}?next={reverse('property_detail', args=[self.property.id])}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Interest.objects.count(), 0)

    def test_tenant_can_express_interest_once(self):
        self.client.force_login(self.tenant)
        response = self.client.post(
            reverse("property_detail", args=[self.property.id]),
            {"message": "I am interested."},
        )
        self.assertRedirects(response, reverse("property_detail", args=[self.property.id]))
        self.assertTrue(Interest.objects.filter(property=self.property, tenant=self.tenant).exists())

    def test_wishlist_change_requires_post(self):
        self.client.force_login(self.tenant)
        response = self.client.get(reverse("toggle_wishlist", args=[self.property.id]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Wishlist.objects.count(), 0)
