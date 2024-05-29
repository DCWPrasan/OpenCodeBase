from django.urls import path
from AuthApp import views

urlpatterns = [
    path("auth/login", views.Login.as_view()),
    path("auth/logout", views.Logout.as_view()),
    path("auth/authorized", views.UserLoginCheck.as_view(), name="user_auth_check"),
    path("auth/profile", views.UserProfileView.as_view()),
]
