from .forms import UserUpdateForm, ProfileUpdateForm
from django.shortcuts import render, redirect
from .forms import RegisterFrom, LoginForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
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


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def edit_profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "accounts/edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        for field in form.fields.values():
            field.widget.attrs.update({"class": "form-control"})

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

        for field in form.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    return render(request, "accounts/change_password.html", {"form": form})