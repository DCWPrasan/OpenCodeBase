from django.urls import path
from DrawingApp import views

urlpatterns = [
    path('drawing', views.DrawingApiView.as_view()),
    path('drawing/<str:id>', views.DrawingApiView.as_view()),
    path('drawing_edit/<str:id>', views.DrawingEditApiView.as_view()),
    path('drawing_size', views.DrawingSizeApiView.as_view()),
    path('drawing_approve', views.ApproveDrawingApiView.as_view()),
    path('drawing_archive', views.ArchiveDrawingApiView.as_view()),
    path('drawing_permanent_delete', views.DrawingPermanentDeleteApiView.as_view()),
    path('drawing_file_upload', views.UploadDrawingFileApiView.as_view()),
    path('drawing_file_download/<str:id>', views.DownalodDrawingFileApiView.as_view()),
    path('drawing_bulk_upload', views.BulkUploadDrawingApiView.as_view()),
    path('drawing_description/<str:drawing_id>', views.DrawingDescriptionApiView.as_view()),
    path('drawing_log', views.DrawingLogApiView.as_view()),
    path('drawing_log/<str:drawing_id>', views.DrawingLogApiView.as_view()),
    path('download_drawing_log_excel', views.DownloadDrawingLogExcelApiView.as_view()),
    path('download_drawing_zip_file', views.DownlaodDrawingZipFile.as_view()),
    path('search/drawing', views.SearchDrawingApiView.as_view()),
    path('bulk_archive_drawing', views.BulkArchiveDrawingApiView.as_view()),

]
