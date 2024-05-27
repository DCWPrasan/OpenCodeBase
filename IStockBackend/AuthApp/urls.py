from django.urls import path
from AuthApp import views

urlpatterns = [
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('authorized', views.UserLoginCheck.as_view(), name='user_auth_check'),
    path('profile', views.UserProfileView.as_view()),
]
