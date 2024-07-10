import logging

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .models import SakanaUser
from .utils import create_sakana_user, sakana_authenticate, sakana_login, sakana_logout

logger = logging.getLogger(__name__)


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
    logger.error(f"Authentication failed with username: {username}, password: {password}")
    err_msg = "Username or password invalid!"
    return JsonResponse({"status": 1, "err_msg": err_msg})


def do_logout(request):
    sakana_logout(request)
    return HttpResponse(status=204)


def do_register(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    display_name = request.POST.get("display-name")
    email = request.POST.get("email")
    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    if not (username and password and display_name):
        err_msg = "Please provide a valid username, password or display name!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    existing_user = User.objects.filter(username=username).first()
    if existing_user:
        err_msg = "User already exists!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    existing_skn_user = SakanaUser.objects.filter(display_name=display_name).first()
    if existing_skn_user:
        err_msg = "Display name already in use!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    try:
        # Create auth User entry
        auth_user = User.objects.create_user(username=username, password=password, email=email,
                                             first_name=first_name, last_name=last_name)
    except Exception as e:  # Let auth backend validate each fields
        logger.error(f"Registration failed: {repr(e)}")
        err_msg = "Username cannot be empty and cannot exceed 150 characters; password cannot exceed 128 " \
                  "characters or too short or insecure; email cannot exceed 254 characters and must be valid;" \
                  "first name and last name cannot exceed 150 characters!"
        return JsonResponse({"status": 1, "err_msg": err_msg})
    # Create SakanaUser entry
    user = create_sakana_user(auth_user, display_name)
    logger.info(f"Registered user {user.id}: {display_name}")
    # Immediately log user in on successful registration
    sakana_login(request, user)
    return JsonResponse({"status": 0})
