from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Inquiry, Property, SellLead


class SubmissionAdminVisibilityTests(TestCase):
    def setUp(self):
        self.user_one = User.objects.create_user(
            username="member_one",
            email="member1@example.com",
            password="secure-pass-123",
        )
        self.user_two = User.objects.create_user(
            username="member_two",
            email="member2@example.com",
            password="secure-pass-456",
        )
        self.admin_user = User.objects.create_superuser(
            username="site_admin",
            email="admin@example.com",
            password="admin-pass-123",
        )
        self.property = Property.objects.create(
            name="Admin Visibility Property",
            location="Colombo",
            price=5000000,
            listing_category="Sell",
            property_type="Residential",
            description="Property used for inquiry submissions.",
        )

    def test_sell_submissions_from_multiple_users_are_saved_and_visible_in_admin(self):
        self.client.force_login(self.user_one)
        response = self.client.post(
            reverse("sell"),
            data={
                "name": "Member One",
                "email": "member1@example.com",
                "phone": "0700000001",
                "property_type": "Residential",
                "location": "Colombo 01",
                "message": "I want to sell my property.",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user_two)
        response = self.client.post(
            reverse("sell"),
            data={
                "name": "Member Two",
                "email": "member2@example.com",
                "phone": "0700000002",
                "property_type": "Apartment",
                "location": "Colombo 02",
                "message": "Looking to list an apartment.",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(SellLead.objects.count(), 2)
        self.assertTrue(SellLead.objects.filter(user=self.user_one, email="member1@example.com").exists())
        self.assertTrue(SellLead.objects.filter(user=self.user_two, email="member2@example.com").exists())

        self.client.force_login(self.admin_user)
        admin_response = self.client.get(reverse("admin:listings_selllead_changelist"))
        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, "member1@example.com")
        self.assertContains(admin_response, "member2@example.com")

    def test_inquiry_submissions_from_multiple_users_are_saved_and_visible_in_admin(self):
        self.client.force_login(self.user_one)
        response = self.client.post(
            reverse("send_inquiry", args=[self.property.pk]),
            data={
                "name": "Member One",
                "email": "member1@example.com",
                "message": "I need more details about this property.",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user_two)
        response = self.client.post(
            reverse("send_inquiry", args=[self.property.pk]),
            data={
                "name": "Member Two",
                "email": "member2@example.com",
                "message": "Can I schedule a visit?",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Inquiry.objects.count(), 2)
        self.assertTrue(
            Inquiry.objects.filter(
                user=self.user_one,
                property=self.property,
                email="member1@example.com",
            ).exists()
        )
        self.assertTrue(
            Inquiry.objects.filter(
                user=self.user_two,
                property=self.property,
                email="member2@example.com",
            ).exists()
        )

        self.client.force_login(self.admin_user)
        admin_response = self.client.get(reverse("admin:listings_inquiry_changelist"))
        self.assertEqual(admin_response.status_code, 200)
        self.assertContains(admin_response, "member1@example.com")
        self.assertContains(admin_response, "member2@example.com")
