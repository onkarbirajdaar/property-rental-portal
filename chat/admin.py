from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "tenant", "created_at")
    list_filter = ("created_at",)
    search_fields = ("tenant__username",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "body", "created_at")
    list_filter = ("created_at",)
    search_fields = ("sender__username", "body")