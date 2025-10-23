from django.urls import path
from AdminApp import views

urlpatterns = [
   # job | Logentry
   path('job/automation', views.AutomationJobView.as_view()),
   path('job/automation/<str:id>', views.AutomationJobView.as_view()),
   
   path('job/powerlab', views.PowerLabJobView.as_view()), 
   path('job/powerlab/<str:id>', views.PowerLabJobView.as_view()),
   path('job/inprogress-powerlab', views.InProgressPowerLabJobView.as_view()),
   
   path('job/repairlab', views.RepairLabJobView.as_view()),
   path('job/repairlab/<str:id>', views.RepairLabJobView.as_view()),
   path('job/inprogress-repairlab', views.InProgressRepairLabJobView.as_view()),
   
   path('job/WeighingMaintenance', views.WeighingMaintenanceJobView.as_view()),
   path('job/WeighingMaintenance/<str:id>', views.WeighingMaintenanceJobView.as_view()),
   
   path('job/WeighingOperation', views.WeighingOperationJobView.as_view()),
   path('job/WeighingOperation/<str:id>', views.WeighingOperationJobView.as_view()),
   
   path('job/cctv',views.CCTVJobView.as_view()),
   path('job/cctv/<str:id>',views.CCTVJobView.as_view()),

   # employee
   path('employees', views.EmployeesView.as_view()),
   path('employees/<str:id>', views.EmployeesView.as_view()),
   path('employees/<str:id>/password-reset/', views.PasswordResetView.as_view(), name='employee_password_reset'),
   path('employees_search/<str:area>', views.EmployeesSearchView.as_view()),
   path('employees_search_table', views.EmployeesSearchTableView.as_view(), name='employee-search-table'),
   
   
   #Report
   #CCTV
   path("cctv_reports/summary/", views.CCTVJobReportAPIView.as_view(), name="cctv-summary-report"),
   
   #Repairlab
   path("repair_lab_reports/summary/", views.RepairLabSummaryReportAPIView.as_view(), name="repair-lab-summary-report"),
   path("repair_lab_reports/person/", views.RepairLabPersonReportAPIView.as_view(), name="repair-lab-person-report"),
   
   
   #Powerlab
   path("power_lab_reports/summary/", views.PowerLabSummaryReportAPIView.as_view(), name="power-lab-summary-report"),
   path("power_lab_reports/person/", views.PowerLabPersonReportAPIView.as_view(), name="power-lab-person-report"),
   
   #WeighingMaintenance
   path("weighing_maintenance_reports/summary/", views.WeighingMaintenanceReportAPIView.as_view(), name="weighing-maintenance-summary-report"),
 
   #WeighingOperation
   path("weighing_operation_reports/summary/", views.WeighingOperationReportAPIView.as_view(), name="weighing-operation-summary-report"),
  
   #Automation
   path("automation_reports/summary/", views.AutomationJobReportAPIView.as_view(), name="automation-summary-report"),
   
   
   
   #Dashboard
   path('powerlab-job-status-counts/', views.PowerLabJobStatusCountView.as_view(), name='powerlab-job-status-counts'),
   path('repairlab-job-status-counts/', views.RepairLabJobStatusCountView.as_view(), name='repairlab-job-status-counts'),
   path('job-counts/', views.JobCountAPIView.as_view(), name='job-counts'),
   path("job-trend/monthly/", views.MonthlyJobTrendAPIView.as_view(), name="monthly-job-trend"),
   path('all-job-counts/', views.AllJobCountAPIView.as_view(), name='all-job-counts'),
   path ('job-counts-by-shift/', views.JobCountByShiftAPIView.as_view(), name='job-counts-by-shift'),
   path ('slide-image/', views.SlideImageAPIView.as_view(), name='sliders'),
   path ('slide-image/<str:id>/', views.SlideImageAPIView.as_view(), name='sliders-details'),
   path ('screener-dashbaord/', views.ScreenerDashboardAPIView.as_view(), name='screener-dashboard'),
   path ('screener-slides/', views.ScreenerSlidesAPIView.as_view(), name='screener-slides'),

   
   ]
