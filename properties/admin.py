from django.contrib import admin
from .models import Property,Interest, Wishlist
# Register your models here.

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "area", "rent", "bhk", "created_at")
    list_filter = ("city", "bhk", "owner")
    search_fields = ("title", "city", "area", "owner__username")


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("property", "tenant", "created_at", "message")
    list_filter = ("created_at", "property")
    search_fields = ("tenant__username", "property__title", "message")

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("property", "user", "created_at")
    list_filter = ("created_at", "property")
    search_fields = ("user__username", "property__title")
    
    

