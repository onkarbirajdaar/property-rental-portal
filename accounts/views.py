from django.shortcuts import render, redirect
from .forms import RegisterFrom, LoginForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
# Create your views here.


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def register(request):

    if request.method == "POST":
        form = RegisterFrom(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect("home")
    else:
        form = RegisterFrom(request.POST)
        return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            next_url = request.GET.get("next")

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url, allowed_hosts={request.get_host()},
            ):
                return redirect(next_url)

            return redirect("home")

    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")
