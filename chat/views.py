from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import MessageForm
from .models import Conversation, Message
from django.http import JsonResponse


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("property", "tenant"),
        id=conversation_id,
    )
    user = request.user
    # Only the tenant or property owner can access the conversation.
    if user.id != conversation.tenant_id and user.id != conversation.property.owner_id:
        return redirect("home")
    messages = conversation.messages.select_related("sender").all()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = user
            message.save()
            return redirect(
                "conversation_detail",
                conversation_id=conversation.id,
            )
    else:
        form = MessageForm()

    return render(
        request,
        "chat/conversation_detail.html",
        {
            "conversation": conversation,
            "messages": messages,
            "form": form,
        },
    )


@login_required
def chat_messages(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("property"),
        id=conversation_id,
    )

    # Only tenant or property owner can access
    if (
        request.user.id != conversation.tenant_id
        and request.user.id != conversation.property.owner_id
    ):
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403,
        )

    messages = conversation.messages.select_related("sender").all()

    return JsonResponse(
        {
            "messages": [
                {
                    "id": message.id,
                    "body": message.body,
                    "sender": message.sender.username,
                    "sender_id": message.sender_id,
                    "created_at": message.created_at.isoformat(),
                }
                for message in messages
            ]
        }
    )

@login_required
def send_message(request, conversation_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405,
        )

    conversation = get_object_or_404(
        Conversation.objects.select_related("property"),
        id=conversation_id,
    )

    if (
        request.user.id != conversation.tenant_id
        and request.user.id != conversation.property.owner_id
    ):
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403,
        )

    body = request.POST.get("body", "").strip()

    if not body:
        return JsonResponse(
            {"error": "Message cannot be empty"},
            status=400,
        )

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        body=body,
    )

    return JsonResponse({
        "id": message.id,
        "body": message.body,
        "sender": message.sender.username,
        "sender_id": message.sender_id,
        "created_at": message.created_at.isoformat(),
    })