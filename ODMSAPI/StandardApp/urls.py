from django.urls import path
from .views import *

urlpatterns = [
    path('standard', StandardAPIView.as_view()),
    path('standard/<str:id>', StandardAPIView.as_view()),
    
    path('rsn_volume', RSNVolumeAPIView.as_view()),
    path('rsn_volume/<str:id>', RSNVolumeAPIView.as_view()),
    
    path('rsn_group', RSNGroupAPIView.as_view()),
    path('rsn_group/<str:id>', RSNGroupAPIView.as_view()),
    
    path('ipss', IPSSAPIView.as_view()),
    path('ipss/<str:id>', IPSSAPIView.as_view()),
    # view file
    path('standard_file_download/<str:id>', DownloadStandardFileApiView.as_view()),
    # search api
    path('search/rsn_group/<str:vol_id>', SearchRsnGroupApiView.as_view()),
    path('search/rsn_group', SearchRsnGroupApiView.as_view()),
    path('search/rsn_volume', SearchRsnVolumeApiView.as_view()),
    path('search/ipsstitle', SearchIPSSTitleApiView.as_view()),
    # approve/archive
    path('standard_approve', ApproveStandardApiView.as_view()),
    path('standard_archive', ArchiveStandardApiView.as_view()),
    # delete standards
    path('standard_permanent_delete', StandardPermanentDeleteApiView.as_view()),
    # log
    path('standard_log', StandardLogApiView.as_view()),
    path('standard_log/<str:standard_id>', StandardLogApiView.as_view()),
    # view log excel
    path('download_standard_log_excel', DownloadStandardLogExcelApiView.as_view()),

    path('standard_bulk_upload', BulkUploadStandardApiView.as_view()),
    #bulk archive
    path('standard_bulk_archive', BulkArchiveStandardApiView.as_view()),
    
    path('standard_count', StandardCountApiView.as_view()),
]