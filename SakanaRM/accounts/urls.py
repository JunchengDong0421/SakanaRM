from django.urls import path

from . import views

urlpatterns = [
    path("login-register/", views.display_login_register_page, name="login-register-page"),

    path("auth/login", views.do_login, name="login-action"),
    path("auth/logout", views.do_logout, name="logout-action"),
    path("auth/register", views.do_register, name="register-action")
]
