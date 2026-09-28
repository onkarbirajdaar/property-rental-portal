from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import Conversation


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