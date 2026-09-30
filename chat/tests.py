from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator

from config.asgi import application
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

	def websocket_communicator(self, user=None):
		headers = []
		if user is not None:
			self.client.force_login(user)
			session_cookie = self.client.cookies["sessionid"].value
			headers = [(b"cookie", f"sessionid={session_cookie}".encode())]
		return WebsocketCommunicator(
			application,
			f"/ws/chat/{self.conversation.id}/",
			headers=headers,
		)

	def test_anonymous_user_cannot_access_chat_http_endpoints(self):
		history_url = reverse(
			"chat_messages",
			kwargs={"conversation_id": self.conversation.id},
		)
		send_url = reverse(
			"send_message",
			kwargs={"conversation_id": self.conversation.id},
		)

		self.assertEqual(self.client.get(history_url).status_code, 302)
		self.assertEqual(
			self.client.post(send_url, {"body": "Anonymous"}).status_code,
			302,
		)

	def test_unrelated_user_cannot_open_conversation_page(self):
		self.client.force_login(self.other_user)

		response = self.client.get(
			reverse(
				"conversation_detail",
				kwargs={"conversation_id": self.conversation.id},
			)
		)

		self.assertRedirects(response, reverse("home"))

	def test_anonymous_websocket_is_rejected(self):
		communicator = self.websocket_communicator()

		connected, close_code = async_to_sync(communicator.connect)()

		self.assertFalse(connected)
		self.assertEqual(close_code, 4001)

	def test_unrelated_user_websocket_is_rejected(self):
		communicator = self.websocket_communicator(self.other_user)

		connected, close_code = async_to_sync(communicator.connect)()

		self.assertFalse(connected)
		self.assertEqual(close_code, 4003)

	def test_related_tenant_can_connect_and_send_over_websocket(self):
		communicator = self.websocket_communicator(self.tenant)

		async def exchange_message():
			connected, _ = await communicator.connect()
			await communicator.send_json_to({"body": "WebSocket message"})
			message = await communicator.receive_json_from()
			await communicator.disconnect()
			return connected, message

		connected, message = async_to_sync(exchange_message)()
		self.assertTrue(connected)
		self.assertEqual(message["body"], "WebSocket message")
		self.assertEqual(message["sender_id"], self.tenant.id)
		self.assertTrue(
			Message.objects.filter(
				conversation=self.conversation,
				body="WebSocket message",
				sender=self.tenant,
			).exists()
		)

	def test_owner_can_send_over_websocket(self):
		communicator = self.websocket_communicator(self.owner)

		async def exchange_message():
			connected, _ = await communicator.connect()
			await communicator.send_json_to({"body": "Owner reply"})
			message = await communicator.receive_json_from()
			await communicator.disconnect()
			return connected, message

		connected, message = async_to_sync(exchange_message)()

		self.assertTrue(connected)
		self.assertEqual(message["body"], "Owner reply")
		self.assertTrue(
			Message.objects.filter(
				conversation=self.conversation,
				sender=self.owner,
				body="Owner reply",
			).exists()
		)

	def test_websocket_broadcasts_message_to_tenant_and_owner(self):
		tenant_client = Client()
		tenant_client.force_login(self.tenant)
		tenant_cookie = tenant_client.cookies["sessionid"].value
		owner_client = Client()
		owner_client.force_login(self.owner)
		owner_cookie = owner_client.cookies["sessionid"].value

		async def exchange_message():
			tenant_communicator = WebsocketCommunicator(
				application,
				f"/ws/chat/{self.conversation.id}/",
				headers=[(b"cookie", f"sessionid={tenant_cookie}".encode())],
			)
			owner_communicator = WebsocketCommunicator(
				application,
				f"/ws/chat/{self.conversation.id}/",
				headers=[(b"cookie", f"sessionid={owner_cookie}".encode())],
			)

			tenant_connected, _ = await tenant_communicator.connect()
			owner_connected, _ = await owner_communicator.connect()
			await tenant_communicator.send_json_to({"body": "Realtime hello"})
			tenant_message = await tenant_communicator.receive_json_from()
			owner_message = await owner_communicator.receive_json_from()
			await tenant_communicator.disconnect()
			await owner_communicator.disconnect()
			return tenant_connected, owner_connected, tenant_message, owner_message

		tenant_connected, owner_connected, tenant_message, owner_message = (
			async_to_sync(exchange_message)()
		)

		self.assertTrue(tenant_connected)
		self.assertTrue(owner_connected)
		self.assertEqual(tenant_message["body"], "Realtime hello")
		self.assertEqual(owner_message["body"], "Realtime hello")
		self.assertEqual(Message.objects.filter(body="Realtime hello").count(), 1)

	def test_invalid_websocket_payload_is_ignored(self):
		communicator = self.websocket_communicator(self.tenant)

		async def send_invalid_payload():
			connected, _ = await communicator.connect()
			await communicator.send_json_to({"body": "x" * 2001})
			await communicator.disconnect()
			return connected

		self.assertTrue(async_to_sync(send_invalid_payload)())
		self.assertEqual(Message.objects.count(), 0)
