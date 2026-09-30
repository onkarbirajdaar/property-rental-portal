from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from properties.models import Property

from .models import Conversation, Message


User = get_user_model()


class ChatHttpTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(
			username="owner",
			password="password",
		)
		self.tenant = User.objects.create_user(
			username="tenant",
			password="password",
		)
		self.other_user = User.objects.create_user(
			username="other",
			password="password",
		)
		self.property = Property.objects.create(
			owner=self.owner,
			title="Test property",
			property_type="Apartment",
			rent=1500,
			deposit=3000,
			bhk=2,
			furnished="Furnished",
			address="1 Test Street",
			city="Test City",
			area="Test Area",
			description="A test property",
			contact_number="1234567890",
			image="properties/test.jpg",
		)
		self.conversation = Conversation.objects.create(
			property=self.property,
			tenant=self.tenant,
		)

	def test_authenticated_user_can_load_message_history(self):
		message = Message.objects.create(
			conversation=self.conversation,
			sender=self.owner,
			body="Is the property still available?",
		)
		self.client.force_login(self.tenant)

		response = self.client.get(
			reverse(
				"chat_messages",
				kwargs={"conversation_id": self.conversation.id},
			)
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["messages"][0]["id"], message.id)
		self.assertEqual(
			response.json()["messages"][0]["body"],
			"Is the property still available?",
		)

	def test_tenant_can_send_message(self):
		self.client.force_login(self.tenant)

		response = self.client.post(
			reverse(
				"send_message",
				kwargs={"conversation_id": self.conversation.id},
			),
			{"body": "I would like to schedule a viewing."},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["sender"], self.tenant.username)
		self.assertTrue(
			Message.objects.filter(
				conversation=self.conversation,
				sender=self.tenant,
				body="I would like to schedule a viewing.",
			).exists()
		)

	def test_owner_can_send_message(self):
		self.client.force_login(self.owner)

		response = self.client.post(
			reverse(
				"send_message",
				kwargs={"conversation_id": self.conversation.id},
			),
			{"body": "Yes, it is available."},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["sender"], self.owner.username)

	def test_empty_message_is_rejected(self):
		self.client.force_login(self.tenant)

		response = self.client.post(
			reverse(
				"send_message",
				kwargs={"conversation_id": self.conversation.id},
			),
			{"body": "   "},
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Message.objects.count(), 0)

	def test_unrelated_user_cannot_read_or_send_messages(self):
		self.client.force_login(self.other_user)
		history_url = reverse(
			"chat_messages",
			kwargs={"conversation_id": self.conversation.id},
		)
		send_url = reverse(
			"send_message",
			kwargs={"conversation_id": self.conversation.id},
		)

		history_response = self.client.get(history_url)
		send_response = self.client.post(send_url, {"body": "Unauthorized"})

		self.assertEqual(history_response.status_code, 403)
		self.assertEqual(send_response.status_code, 403)
		self.assertEqual(Message.objects.count(), 0)
