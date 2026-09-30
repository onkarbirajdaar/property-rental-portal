from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Conversation, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		user = self.scope.get("user")
		if not user or user.is_anonymous:
			await self.close(code=4001)
			return

		conversation = await self.get_authorized_conversation(
			self.scope["url_route"]["kwargs"]["conversation_id"],
			user.id,
		)
		if conversation is None:
			await self.close(code=4003)
			return

		group_name = f"chat_{self.scope['url_route']['kwargs']['conversation_id']}"
		await self.channel_layer.group_add(group_name, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		group_name = f"chat_{self.scope['url_route']['kwargs']['conversation_id']}"
		await self.channel_layer.group_discard(
			group_name,
			self.channel_name,
		)

	async def receive_json(self, content, **kwargs):
		body = content.get("body", "")
		if not isinstance(body, str):
			await self.send_json({"error": "Message body must be text."})
			return

		body = body.strip()
		if not body or len(body) > 2000:
			await self.send_json({"error": "Message cannot be empty."})
			return

		session_user_id = self.scope.get("session", {}).get("_auth_user_id")
		if not session_user_id:
			return

		message = await self.create_message(body, int(session_user_id))
		group_name = f"chat_{self.scope['url_route']['kwargs']['conversation_id']}"
		await self.channel_layer.group_send(
			group_name,
			{
				"type": "chat.message",
				"id": message["id"],
				"body": message["body"],
				"sender": message["sender"],
				"sender_id": message["sender_id"],
				"created_at": message["created_at"],
			},
		)

	async def chat_message(self, event):
		await self.send_json(
			{
				"id": event["id"],
				"body": event["body"],
				"sender": event["sender"],
				"sender_id": event["sender_id"],
				"created_at": event["created_at"],
			}
		)

	@database_sync_to_async
	def get_authorized_conversation(self, conversation_id, user_id):
		conversation = (
			Conversation.objects.select_related("property")
			.filter(id=conversation_id)
			.first()
		)
		if conversation is None:
			return None

		if user_id not in {conversation.tenant_id, conversation.property.owner_id}:
			return None

		return conversation

	@database_sync_to_async
	def create_message(self, body, user_id):
		message = Message.objects.create(
			conversation_id=self.scope["url_route"]["kwargs"]["conversation_id"],
			sender_id=user_id,
			body=body,
		)
		return {
			"id": message.id,
			"body": message.body,
			"sender": message.sender.username,
			"sender_id": message.sender_id,
			"created_at": message.created_at.isoformat(),
		}
