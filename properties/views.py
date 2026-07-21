from django.shortcuts import render, get_object_or_404, redirect
from .models import Property
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PropertyForm
# Create your views here.


def home(request):
    properties = Property.objects.all()
    city = request.GET.get("city")
    area = request.GET.get("area")
    bhk = request.GET.get("bhk")
    sort = request.GET.get("sort", "")
    if city:
        properties = properties.filter(city__icontains=city)
    if area:
        properties = properties.filter(area__icontains=area)
    if bhk:
        properties = properties.filter(bhk=bhk)
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
    return render(request, "home.html", {"page_obj": page_obj, "sort": sort, "city": city, "bhk": bhk, "area": area, "query_string": query_string})


def property_detail(request, id):
    property = get_object_or_404(Property, id=id)
    return render(request, "property_detail.html", {"property": property})


@login_required
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