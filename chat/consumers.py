from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation


class ChatConsumer(AsyncWebsocketConsumer):
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

		self.conversation_id = conversation.id
		self.group_name = f"chat_{self.conversation_id}"
		await self.channel_layer.group_add(self.group_name, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		if hasattr(self, "group_name"):
			await self.channel_layer.group_discard(
				self.group_name,
				self.channel_name,
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
