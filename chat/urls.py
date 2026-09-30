from django.urls import path

from . import views
urlpatterns = [
    path(
        "conversation/<int:conversation_id>/",
        views.conversation_detail,
        name="conversation_detail",
    ),

    path(
        "conversation/<int:conversation_id>/messages/",
        views.chat_messages,
        name="chat_messages",
    ),
    path(
    "conversation/<int:conversation_id>/send/",
    views.send_message,
    name="send_message",
),
]