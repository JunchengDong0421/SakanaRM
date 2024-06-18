from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.display_login_page, name="login-page"),
    path("logout/", views.display_logout_page, name="logout-page"),
    path("register/", views.display_register_page, name="register-page"),

    path("auth/login", views.do_login, name="login-action"),
    path("auth/logout", views.do_logout, name="logout-action"),
    path("auth/register", views.do_register, name="register-action")
]
