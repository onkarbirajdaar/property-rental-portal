from django.shortcuts import render, get_object_or_404, redirect
from functools import wraps
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Property
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PropertyForm, InterestForm
from .models import Property, PROPERTY_TYPES, FURNISHED_CHOICES, Interest, STATUS_CHOICES, Wishlist


def owner_required(view_func):
    """Limit listing management actions to users registered as owners."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.profile.role != "owner":
            messages.error(request, "Only property owners can post a property.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapped_view


def home(request):
    properties = Property.objects.all().filter(status="Available")
   
    city = request.GET.get("city")
    area = request.GET.get("area")
    bhk = request.GET.get("bhk")
    min_rent = request.GET.get("min_rent")
    max_rent = request.GET.get("max_rent")
    property_type = request.GET.get("property_type")
    furnished = request.GET.get("furnished")
    sort = request.GET.get("sort", "")
    if city:
        properties = properties.filter(city__icontains=city)
    if area:
        properties = properties.filter(area__icontains=area)
    if bhk:
        properties = properties.filter(bhk=bhk)
    if min_rent:
        properties = properties.filter(rent__gte=min_rent)
    if max_rent:
        properties = properties.filter(rent__lte=max_rent)
    if property_type:
        properties = properties.filter(property_type=property_type)    
    if furnished:
        properties = properties.filter(furnished=furnished)              
    if sort == "rent_low":
        properties = properties.order_by("rent")
    elif sort == "rent_high":
        properties = properties.order_by("-rent")
    else:
        properties = properties.order_by("-created_at")
    paginator = Paginator(properties, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    query_string = query_params.urlencode()
    return render(request, "home.html", {
        "page_obj": page_obj,
        "sort": sort,
        "city": city,
        "bhk": bhk,
        "area": area,
        "min_rent": min_rent,
        "max_rent": max_rent,
        "property_type": property_type,
        "furnished": furnished,
        "query_string": query_string,
        "property_types": PROPERTY_TYPES,
        "furnished_choices": FURNISHED_CHOICES,
        
})

def property_detail(request, id):
    property = get_object_or_404(Property, id=id)
    is_owner = request.user == property.owner
    if is_owner:
        interests = property.interests.all().order_by("-created_at")
    else:
        interests = None
    if request.user.is_authenticated:
        already_interested = Interest.objects.filter(property=property, tenant=request.user).exists()
    else:
        already_interested = False

    form = InterestForm()  # default blank form for GET requests

    if request.method == "POST" and not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    if request.method == "POST" and not is_owner and not already_interested:
        form = InterestForm(request.POST)
        if form.is_valid():
            interest = form.save(commit=False)
            interest.property = property
            interest.tenant = request.user
            interest.save()
            messages.success(request, "Interest sent to the owner.")
            return redirect("property_detail", id=property.id)

    if request.user.is_authenticated:
        already_wishlisted = Wishlist.objects.filter(property=property, user=request.user).exists()
    else:
        already_wishlisted = False

    return render(request, "property_detail.html", {
        "property": property,
        "is_owner": is_owner,
        "already_interested": already_interested,
        "form": form,
        "interests": interests,
        "already_wishlisted": already_wishlisted,
    })


     


@login_required
@owner_required
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()

            messages.success(request, "Property added successfully.")
            return redirect("dashboard")
    else:
        form = PropertyForm()

    return render(request, "add_property.html", {"form": form})


@login_required
def my_properties(request):
    properties = request.user.properties.all().order_by("-created_at")

    return render(request, "properties/my_properties.html", {
        "properties": properties,
    })

@login_required
def edit_property(request, id):
    property = get_object_or_404(Property, id=id)
    if property.owner != request.user:
        messages.error(request, "You are not authorized to edit this property.")
        return redirect("my_properties")
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property edited successfully.")
            return redirect("dashboard")
    else:
        form = PropertyForm(instance=property)        
    return render(request, "edit_property.html", {"form": form,"property":property})

@login_required
def delete_property(request, id):
    property = get_object_or_404(Property, id=id)
    if property.owner != request.user:
        messages.error(request, "You are not authorized to delete this property.")
        return redirect("my_properties")
    if request.method == "POST":
        property.delete()
        messages.success(request, "Property deleted")
        return redirect("my_properties")
           
    return render(request, "delete_property.html", {"property":property})


@login_required
@require_POST
def toggle_wishlist(request, id):
    property = get_object_or_404(Property, id=id)
    if property.owner == request.user:
        messages.error(request, "You cannot add your own property to your wishlist.")
        return redirect("property_detail", id=property.id)

    wishlist_item = Wishlist.objects.filter(property=property, user=request.user).first()

    if wishlist_item:
        wishlist_item.delete()   
        messages.success(request, "Removed from wishlist.")
    else:
        Wishlist.objects.create(property=property, user=request.user)   
        messages.success(request, "Added to wishlist.")

    return redirect("property_detail", id=property.id)


@login_required
def my_wishlist(request):
    wishlist_items = request.user.wishlists.all().order_by("-created_at")
    return render(request, "properties/my_wishlist.html", {
        "wishlist_items": wishlist_items,
    })
