from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.generic import ListView


# Create your views here.

def home_page(request):
    username = request.user.get_username() if request.user.is_authenticated else None
    return render(request, "core/index.html", {"username": username})
