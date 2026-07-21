from django.contrib import admin
from .models import Property
# Register your models here.

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "area", "rent", "bhk", "created_at")
    list_filter = ("city", "bhk", "owner")
    search_fields = ("title", "city", "area", "owner__username")
