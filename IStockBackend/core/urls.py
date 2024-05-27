"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
import os
from rest_framework.response import Response
from rest_framework.decorators import api_view

def home(request):
    return HttpResponse("Welcome to home page!")

@api_view(['GET'])
def serve_drawing_file(request, drawing_type, file_name):
    return Response({"detail": "File not found."}, status=404)


urlpatterns = [
    path('api/auth/', include('AuthApp.urls')),
    path('api/', include('DrawingApp.urls')),
    path('api/', include('AdminApp.urls')),
    path('api/', include('StandardApp.urls')),
    path('api/', include('ManualApp.urls')),
    path('api/', include('NoticeApp.urls')),
    path('api/', include('SIApp.urls')),
    path('', home),
    path('media/drawings/<str:drawing_type>/<str:file_name>', serve_drawing_file),
    path('media/drawings/<str:drawing_type>/<str:file_name>/', serve_drawing_file)
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

