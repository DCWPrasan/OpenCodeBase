from django.urls import path
from .views import (
    ManualAPIView,
    DownloadManualFileApiView,
    ManualLogApiView,
    DownloadManualLogExcelApiView,
    ApproveManualApiView,
    ArchiveManualApiView,
    BulkArchiveManualApiView,
    ManualPermanentDeleteApiView,
    BulkUploadManualApiView,
    ManualCountApiView,
    )


urlpatterns = [
    path('manual',ManualAPIView.as_view()),
    path('manual/<str:id>',ManualAPIView.as_view()),
    # file
    path('manual_file_download/<str:id>',DownloadManualFileApiView.as_view()),
    # approve/archive
    path('manual_approve', ApproveManualApiView.as_view()),
    path('manual_archive', ArchiveManualApiView.as_view()),
    # delete
    path('manual_permanent_delete', ManualPermanentDeleteApiView.as_view()),
    # log
    path('manual_log',ManualLogApiView.as_view()),
    path('manual_log/<str:manual_id>',ManualLogApiView.as_view()),
    # view log excel
    path('download_manual_log_excel', DownloadManualLogExcelApiView.as_view()),
    # bulk archive
    path('manual_bulk_archive', BulkArchiveManualApiView.as_view()),
    # bulk upload
    path('manual_bulk_upload', BulkUploadManualApiView.as_view()),
    path('manual_count', ManualCountApiView.as_view()),
]