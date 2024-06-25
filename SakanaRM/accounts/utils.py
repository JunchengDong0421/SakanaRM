from django.contrib.auth import authenticate, login, logout

from .models import SakanaUser


def create_sakana_user(auth_user):  # create SakanaUser from User
    user = SakanaUser(auth_user=auth_user)
    user.save()
    return user


def sakana_authenticate(request, **credentials):  # returns a RMUser object
    auth_user = authenticate(request, **credentials)
    if auth_user is None:
        return
    username = auth_user.get_username()
    user = SakanaUser.objects.filter(auth_user__username=username).first()
    return user


def sakana_login(request, user, backend=None):  # takes in a RMUser object
    auth_user = user.auth_user
    login(request, auth_user, backend)
    request.session["uid"] = user.id


def sakana_logout(request):
    if request.session.get("uid"):
        request.session.pop("uid")
    logout(request)
