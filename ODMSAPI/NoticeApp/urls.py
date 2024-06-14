from django.urls import path
from .views import (
   NoticeApiView,
   NoticeOpenApiView,
   SliderApiView,
   SliderOpenApiView,
   NewUserReuqestApiView,
   CreateNewUserRequestApiView,
   DrawingCountApiView

)


urlpatterns = [
   path('notice', NoticeApiView.as_view()),
   path('open_notice', NoticeOpenApiView.as_view()),
   path("open_count_dashboard", DrawingCountApiView.as_view()),
   path('slider', SliderApiView.as_view()),
   path('slider/<str:id>', SliderApiView.as_view()),
   path('open_slider', SliderOpenApiView.as_view()),
   path('new_user_request', NewUserReuqestApiView.as_view()),
   path('create_new_user_request', CreateNewUserRequestApiView.as_view()),
   path('create_new_user_request/<str:personnel_number>', CreateNewUserRequestApiView.as_view()),
]