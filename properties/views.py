from django.shortcuts import render, get_object_or_404
from .models import Property
from django.core.paginator import Paginator
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
