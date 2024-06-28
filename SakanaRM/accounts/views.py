from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .utils import create_sakana_user, sakana_authenticate, sakana_login, sakana_logout


def display_login_register_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "accounts/login_register.html")


def do_login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = sakana_authenticate(request, username=username, password=password)
    if user is not None:
        sakana_login(request, user)
        return JsonResponse({"status": 0})
    err_msg = "Username or password invalid!"
    return JsonResponse({"status": 1, "err_msg": err_msg})


def do_logout(request):
    sakana_logout(request)
    return HttpResponse(status=204)


def do_register(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    email = request.POST.get("email")
    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    existing_user = User.objects.filter(username=username)
    if existing_user:
        err_msg = "User already exists!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        # Create auth User entry
        auth_user = User.objects.create_user(username=username, password=password, email=email,
                                             first_name=first_name, last_name=last_name)
    except:
        err_msg = "Username cannot be empty and cannot exceed 150 characters; password cannot exceed 128 " \
                  "characters or too short or insecure; email cannot exceed 254 characters and must be valid;" \
                  "first name and last name cannot exceed 150 characters!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # Create SakanaUser entry
    user = create_sakana_user(auth_user)
    # Immediately log user in on successful registration
    sakana_login(request, user)
    return JsonResponse({"status": 0})
