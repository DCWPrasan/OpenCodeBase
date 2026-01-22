# urls.py
from django.urls import path
from .views import (
    T72ListCreateAPIView,
    T72DetailAPIView,
    T72IssueAPIView,
    T72DashboardAPIView,
    SearchUserAPIView,
    T72RemarkAPIView,
    T72IssuedHistoryListAPIView,
    T72IssuedHistoryExportAPIView,
)

urlpatterns = [
    path("t72/", T72ListCreateAPIView.as_view()),
    path("t72/dashboard/", T72DashboardAPIView.as_view()),
    path("t72/history/", T72IssuedHistoryListAPIView.as_view()),
    path("t72/history/export/", T72IssuedHistoryExportAPIView.as_view()),
    path("t72/<str:pk>/", T72DetailAPIView.as_view()),
    path("t72/<str:pk>/issue/", T72IssueAPIView.as_view()),
    path("t72/<str:pk>/remarks/", T72RemarkAPIView.as_view()),
    path("search/users", SearchUserAPIView.as_view()),
]
