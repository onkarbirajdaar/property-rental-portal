from django.shortcuts import render
from .models import Property
# Create your views here.


def home(request):
    properties = Property.objects.all()
    return render(request, "home.html", {"properties": properties})
