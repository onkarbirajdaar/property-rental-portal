from django.urls import path
from . import views
# from .views import property_detail

urlpatterns = [
    path("", views.home, name="home"),
    path("property/<int:id>/", views.property_detail, name="property_detail"),
    path("properties/add/", views.add_property, name="add_property"),
    path("properties/my/", views.my_properties, name="my_properties"),
    path("properties/<int:id>/edit/", views.edit_property, name="edit_property"),
]   
