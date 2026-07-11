from django.urls import path
from . import views
# from .views import property_detail

urlpatterns = [
    path("", views.home, name="home"),
    path("property/<int:id>/", views.property_detail, name="property_detail")
]
