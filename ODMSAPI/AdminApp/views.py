from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from AuthApp.pagination import CustomPagination
from AuthApp.models import User, Department, Unit, LogInOutLog, Subvolume, Volume
from SIApp.models import SIR, StabilityCertification, Compliance
from StandardApp.models import Standard, StandardLog
from ManualApp.models import Manual, ManualLog
from SIApp.models import SIRLog, StabilityCertificationLog, ComplianceLog
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from core.utility import Syserror, parse_user_agent
from datetime import datetime, timedelta
from AdminApp.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserLoginLogoutLogListSerializer,
    DepartmentSerializer,
    UnitSerializer,
    SearchDepartmentSerializer,
    SearchUnitSerializer,
    SearchUserSerializer,
    SearchVolumeSerializer,
    SubVolumeSerializer,
    VolumeSerializer,
    SearchRSVolumeSerializer
)
import re

from DrawingApp.serializers import DrawingLogListSerializer
from ManualApp.serializers import ManualLogSerializer
from StandardApp.serializers import StandardLogSerializer
from SIApp.serializers import SIRLogSerializer, StabilityCertificationLogSerializer, ComplianceLogSerializer
from DrawingApp.models import DrawingLog, Drawing
from AuthApp.customAuth import allowed_admin_user


class DashboardApiView(APIView):

    def get(self, request):
        try:
            # retrive list of user object according to filter_criteria
            today = datetime.now().date()            
            drawing_log_count = DrawingLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status__in=['View Drawing', 'Download Drawing']).count()
            standard_log_count = StandardLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status = "View Standard").count()
            document_log_count = ManualLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status = "View Document").count()
            sir_log_count = SIRLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status = "View SIR").count()
            sc_log_count = StabilityCertificationLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status = "View Stability Certificate").count()
            compliance_log_count = ComplianceLog.objects.values('id').filter(user__is_superuser = False, action_time__date=today, status = 'View Compliance').count()
            data = {
                "log_count": {
                    "drawing": drawing_log_count,
                    "standard": standard_log_count,
                    "document": document_log_count,
                    "si": sir_log_count + sc_log_count + compliance_log_count,
                }
            }
            if request.user.is_superuser:
                drawing_logs = DrawingLog.objects.filter(user = request.user, action_time__date=today).order_by('-action_time')[:10]
                data['drawing_log']  = DrawingLogListSerializer(drawing_logs, many=True).data
                drawing_counts = Drawing.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )

                data["drawing_count"] = {
                    "pending": drawing_counts["pending"] or 0,
                    "approved": drawing_counts["approved"] or 0,
                    "archived": drawing_counts["archived"] or 0,
                }
                
                standard_counts = Standard.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )

                data["standard_count"] = {
                    "pending": standard_counts["pending"] or 0,
                    "approved": standard_counts["approved"] or 0,
                    "archived": standard_counts["archived"] or 0,
                }
                
                manual_count = Manual.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )

                data["manual_count"] = {
                    "pending": manual_count["pending"] or 0,
                    "approved": manual_count["approved"] or 0,
                    "archived": manual_count["archived"] or 0,
                }
                
                sir_count = SIR.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )
                
                data["sir_count"] = {
                    "pending": sir_count["pending"] or 0,
                    "approved": sir_count["approved"] or 0,
                    "archived": sir_count["archived"] or 0,
                }

                stability_certificate_count = StabilityCertification.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )
                
                data["stability_certificate_count"] = {
                    "pending": stability_certificate_count["pending"] or 0,
                    "approved": stability_certificate_count["approved"] or 0,
                    "archived": stability_certificate_count["archived"] or 0,
                }

                compliance_count = Compliance.objects.aggregate(
                    pending=Count("id", filter=Q(is_approved=False, is_archive=False)),
                    approved=Count("id", filter=Q(is_approved=True, is_archive=False)),
                    archived=Count("id", filter=Q(is_archive=True)),
                )
                
                data['compliance_count'] = {
                    "pending": compliance_count["pending"] or 0,
                    "approved": compliance_count["approved"] or 0,
                    "archived": compliance_count["archived"] or 0,
                }

            if request.user.role != "User":
                top_10_users = User.objects.filter(loginoutlog__message="Login", is_superuser=False).only('id', 'full_name').annotate(log_count=Count('loginoutlog')).order_by('-log_count')[:10]
                most_user_login = []
                for user in top_10_users:
                    most_user_login.append({
                        "id": user.id,
                        "full_name": user.full_name,
                        "log_count": user.log_count
                    })
                data["most_user_login"] = most_user_login
                
            response = {"success": True, "message": "Dashboard data", "results": data}
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)



class VisitorCountApiView(APIView):

    def get(self, request):
        try:
            today = datetime.now()
            loginlog = LogInOutLog.objects.only('message').filter(message = "Login")
            today_visitor = loginlog.filter(action_time__date = today.date()).count()
            user = User.objects.filter(is_superuser = False).only('id')
            online_user = user.filter(Q(last_login__gt = (today-timedelta(hours=1))) | Q(jti_token__isnull = False) ).count()
            data = {
                "today_visitor": today_visitor,
                "total_visitor": loginlog.count(),
                "total_user":user.count(),
                "online_user": online_user

            }

            response = {"success": True, "message": "Dashbaord data", "results": data}
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DashboardDrawingLogGraphView(APIView):
    def get(self, request):
        try:
            time_period = request.GET.get("time_period", "weekly")
            drawing_log_count = []
            labels = []

            from_date = datetime.now().date()
            if time_period == "weekly":
                to_date = from_date - timedelta(days=6)
            else:
                to_date = from_date - timedelta(days=30)

            date_list = [to_date + timedelta(days=x) for x in range((from_date - to_date).days + 1)]

            log_items = DrawingLog.objects.filter(action_time__date__in=date_list, user__is_superuser = False, status__in = ["View Drawing", "Download Drawing"]).values("action_time__date").annotate(
                log_count=Coalesce(Count("id"), 0)
            )

            log_dict = {item["action_time__date"]: item for item in log_items}

            for date in date_list:
                log_item = log_dict.get(date, {"log_count": 0})
                drawing_log_count.append(log_item["log_count"])
                labels.append(date.strftime("%d-%b"))

            data = {
                "labels": labels,
                "drawing_log_count":{"name": "Drawings Count", "data": drawing_log_count},
            }
            response = {
                "success": True,
                "message": "Dashboard Drawing Log Graph",
                "results": data,
            }
            return Response(response, status=200)
        except Exception as e:
            # Log the error properly
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class DashboardLogInGraphView(APIView):
    def get(self, request):
        try:

            login_data = []
            labels = []

            from_date = datetime.now().date()
            to_date = from_date - timedelta(days=30)

            date_list = [to_date + timedelta(days=x) for x in range((from_date - to_date).days + 1)]

            filter_criteria = Q(action_time__date__in=date_list, user__is_superuser = False, message = "Login")
            log_items = LogInOutLog.objects.filter(filter_criteria).values("action_time__date").annotate(view=Coalesce(Count("id"), 0))

            log_dict = {item["action_time__date"]: item for item in log_items}

            for date in date_list:
                log_item = log_dict.get(date, {"view": 0})
                login_data.append(log_item["view"])
                labels.append(date.strftime("%d-%b"))

            data = {
                "labels": labels,
                "weekly":{"name": "Login Count", "data": login_data[-7:]},
                "monthly":{"name": "Login Count", "data": login_data}
            }
            response = {
                "success": True,
                "message": "Dashboard Standard Log Graph",
                "results": data,
            }
            return Response(response, status=200)
        except Exception as e:
            # Log the error properly
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class DashboardStandardLogGraphView(APIView):
    def get(self, request):
        try:
            time_period = request.GET.get("time_period", "weekly")
            log_views = []
            labels = []
            from_date = datetime.now().date()
            if time_period == "weekly":
                to_date = from_date - timedelta(days=6)
            else:
                to_date = from_date - timedelta(days=30)

            date_list = [to_date + timedelta(days=x) for x in range((from_date - to_date).days + 1)]

            log_items = StandardLog.objects.filter(action_time__date__in=date_list, user__is_superuser = False, status = "View Standard").values("action_time__date").annotate(view=Coalesce(Count("id"), 0))

            log_dict = {item["action_time__date"]: item for item in log_items}

            for date in date_list:
                log_item = log_dict.get(date, {"view": 0})
                log_views.append(log_item["view"])
                labels.append(date.strftime("%d-%b"))

            data = {
                "labels": labels,
                "standard_count":{"name": "Standards Count", "data": log_views}
            }
            response = {
                "success": True,
                "message": "Dashboard Standard Log Graph",
                "results": data,
            }
            return Response(response, status=200)
        except Exception as e:
            # Log the error properly
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DashboardManualLogGraphView(APIView):
    def get(self, request):
        try:
            time_period = request.GET.get("time_period", "weekly")
            log_views = []
            labels = []

            from_date = datetime.now().date()
            if time_period == "weekly":
                to_date = from_date - timedelta(days=6)
            else:
                to_date = from_date - timedelta(days=30)

            date_list = [to_date + timedelta(days=x) for x in range((from_date - to_date).days + 1)]
            log_items = ManualLog.objects.filter(action_time__date__in=date_list, user__is_superuser = False, status = "View Document").values("action_time__date").annotate(view=Coalesce(Count("id"), 0))

            log_dict = {item["action_time__date"]: item for item in log_items}

            for date in date_list:
                log_item = log_dict.get(date, {"view": 0})
                log_views.append(log_item["view"])
                labels.append(date.strftime("%d-%b"))

            data = {
                "labels": labels,
                "document_count":{"name": "Documents Count", "data": log_views}
            }
            response = {
                "success": True,
                "message": "Dashboard Documents Log Graph",
                "results": data,
            }
            return Response(response, status=200)
        except Exception as e:
            # Log the error properly
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class DashboardSILogGraphView(APIView):
    def get(self, request):
        try:
            time_period = request.GET.get("time_period", "weekly")
            si_type = request.GET.get("si_type", "SIR")
            log_views = []
            labels = []

            from_date = datetime.now().date()
            if time_period == "weekly":
                to_date = from_date - timedelta(days=6)
            else:
                to_date = from_date - timedelta(days=30)

            date_list = [to_date + timedelta(days=x) for x in range((from_date - to_date).days + 1)]

            if si_type == "SIR":
                filter_criteria = Q(action_time__date__in=date_list, user__is_superuser = False, status="View SIR")
                log_items = SIRLog.objects.filter(filter_criteria).values("action_time__date").annotate(view=Coalesce(Count("id"), 0))
            elif si_type == "STABILITY CERTIFICATE":
                filter_criteria = Q(action_time__date__in=date_list, user__is_superuser = False, status="View Stability Certificate")
                log_items = StabilityCertificationLog.objects.filter(filter_criteria).values("action_time__date").annotate(view=Coalesce(Count("id"), 0))
            else:
                filter_criteria = Q(action_time__date__in=date_list, user__is_superuser = False, status="View Compliance")
                log_items = ComplianceLog.objects.filter(filter_criteria).values("action_time__date").annotate(view=Coalesce(Count("id"), 0))

            log_dict = {item["action_time__date"]: item for item in log_items}

            for date in date_list:
                log_item = log_dict.get(date, {"view": 0})
                log_views.append(log_item["view"])
                labels.append(date.strftime("%d-%b"))

            data = {
                "labels": labels,
                "si_count": {"name": f"{si_type} Count", "data": log_views},
            }
            response = {
                "success": True,
                "message": "Dashboard SI Log Graph",
                "results": data,
            }
            return Response(response, status=200)
        except Exception as e:
            # Log the error properly
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


# Create your views here.
class UserApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = UserListSerializer

    @allowed_admin_user
    def get(self, request, id=None):
        try:
            # retrive single object of user model
            if id:
                try:
                    instance = User.objects.get(id=id, is_superuser=False)
                except User.DoesNotExist:
                    response = {"success": False, "message": "User does not exist."}
                    return Response(response, status=400)
                serializer = UserDetailSerializer(instance)
                response = {
                    "success": True,
                    "message": "User retrieved successfully",
                    "results": serializer.data,
                }
                return Response(response, status=200)

            # retrive list of user object according to filter_criteria
            filter_criteria = Q(is_superuser=False)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(full_name__icontains=query)
                    | Q(email__icontains=query)
                    | Q(personnel_number__icontains=query)
                    | Q(phone_number__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(department__department_id__icontains=query)
                    | Q(designation__icontains=query)
                    | Q(role__icontains=query)
                )

            instance = (
                User.objects.select_related('department')
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = UserListSerializer(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = UserListSerializer(instance, many=True)
            return Response({"results": serializer.data}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            full_name = data.get("full_name", None)
            password = data.get("password", None)
            email = data.get("email", None)
            phone_number = data.get("phone_number", None)
            personnel_number = data.get("personnel_number", None)
            role = data.get("role", "User")
            department_id = data.get("department_id", None)
            designation = data.get("designation", None)
            is_download_drawing = data.get("is_download_drawing", "NO") == "YES"
            is_view_layout = data.get("is_view_layout", "NO") == "YES"
            is_view_standard = data.get("is_view_standard", "NO") == "YES"
            is_view_manual = data.get("is_view_manual", "NO") == "YES"
            is_view_technical_calculation = data.get("is_view_technical_calculation", "NO") == "YES"
            is_design_user = data.get("is_design_user", "NO") == "YES"
            is_disable_dwg_file = data.get("is_disable_dwg_file", "NO") == "YES"
            if role == "Admin":
                is_download_drawing = True
                is_view_layout = True
                is_view_standard = True
                is_view_manual = True
                is_disable_dwg_file = False
                is_design_user = True
                is_view_technical_calculation=True
            
            if is_design_user:
                is_view_layout = True
                is_view_standard = True
                is_view_manual = True
                is_view_technical_calculation=True
            
            if is_disable_dwg_file:
                is_download_drawing = False
                
            if not is_view_manual:
                is_view_technical_calculation = False
                
            if not all(
                [
                    full_name,
                    password,
                    personnel_number,
                    email,
                    phone_number,
                    role,
                    department_id,
                    designation,
                ]
            ):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required.",
                }
                return Response(response, status=400)

            email_pattern = re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
            )
            if not email_pattern.match(email):
                response = {
                    "success": False,
                    "message": "Invalid email format.",
                }
                return Response(response, status=400)

            if not isinstance(phone_number, int) or len(str(phone_number)) != 10:
                response = {
                    "success": False,
                    "message": "Invalid phone number, require 10 digits.",
                }
                return Response(response, status=400)

            if role not in ["Admin", "User"]:
                response = {
                    "success": False,
                    "message": "Invalid role.",
                }
                return Response(response, status=400)

            if User.objects.filter(email=email).exists():
                response = {
                    "success": False,
                    "message": "Email already exists.",
                }
                return Response(response, status=400)
            if User.objects.filter(phone_number=phone_number).exists():
                response = {
                    "success": False,
                    "message": "Phone number already exists.",
                }
                return Response(response, status=400)
            if User.objects.filter(personnel_number=personnel_number).exists():
                response = {
                    "success": False,
                    "message": "Personnel number already exists.",
                }
                return Response(response, status=400)
            departments = Department.objects.filter(department_id=department_id)
            if not departments.exists():
                response = {
                    "success": False,
                    "message": "Department not found",
                }
                return Response(response, status=400)
            with transaction.atomic():
                instance = User.objects.create_user(
                    full_name=full_name,
                    email=email,
                    phone_number=phone_number,
                    personnel_number=personnel_number,
                    password=password,
                    role=role,
                    department=departments.first(),
                    designation=designation,
                    is_download_drawing=is_download_drawing,
                    is_view_layout=is_view_layout,
                    is_view_standard = is_view_standard,
                    is_view_manual = is_view_manual,
                    is_disable_dwg_file=is_disable_dwg_file,
                    is_view_technical_calculation=is_view_technical_calculation,
                    is_design_user = is_design_user,
                    is_staff=True,
                    is_active=True,
                )
                response = {
                    "success": True,
                    "message": "User created  successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            user_id = data.get("id", None)
            full_name = data.get("full_name", None)
            email = data.get("email", None)
            phone_number = data.get("phone_number", None)
            personnel_number = data.get("personnel_number", None)
            role = data.get("role", "User")
            department_id = data.get("department_id", None)
            designation = data.get("designation", None)
            is_download_drawing = data.get("is_download_drawing", "NO") == "YES"
            is_view_layout = data.get("is_view_layout", "NO") == "YES"
            is_view_standard = data.get("is_view_standard", "NO") == "YES"
            is_view_manual = data.get("is_view_manual", "NO") == "YES"
            is_view_technical_calculation = data.get("is_view_technical_calculation", "NO") == "YES"
            is_design_user = data.get("is_design_user", "NO") == "YES"
            is_disable_dwg_file = data.get("is_disable_dwg_file", "NO") == "YES"
            if role == "Admin":
                is_download_drawing = True
                is_view_layout = True
                is_view_standard = True
                is_view_manual = True
                is_disable_dwg_file = False
                is_design_user = True
                is_view_technical_calculation=True
            
            if is_design_user:
                is_view_layout = True
                is_view_standard = True
                is_view_manual = True
                is_view_technical_calculation=True
            
            if is_disable_dwg_file:
                is_download_drawing = False
                
            if not is_view_manual:
                is_view_technical_calculation = False


            if not all(
                [
                    user_id,
                    full_name,
                    personnel_number,
                    email,
                    phone_number,
                    role,
                    department_id,
                    designation,
                ]
            ):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required.",
                }
                return Response(response, status=400)

            email_pattern = re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
            )
            if not email_pattern.match(email):
                response = {
                    "success": False,
                    "message": "Invalid email format.",
                }
                return Response(response, status=400)

            if not isinstance(phone_number, int) and len(str(phone_number)) != 10:
                response = {
                    "success": False,
                    "message": "Invalid phone number, require 10 digits.",
                }
                return Response(response, status=400)

            if role not in ["Admin", "User"]:
                response = {
                    "success": False,
                    "message": "Invalid role.",
                }
                return Response(response, status=400)
            try:
                instance = User.objects.get(id=user_id)
            except User.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Invalid user id",
                }
                return Response(response, status=400)

            if User.objects.filter(email=email).exclude(email=instance.email).exists():
                response = {
                    "success": False,
                    "message": "Email already exists.",
                }
                return Response(response, status=400)
            if (
                User.objects.filter(phone_number=phone_number)
                .exclude(phone_number=instance.phone_number)
                .exists()
            ):
                response = {
                    "success": False,
                    "message": "Phone number already exists.",
                }
                return Response(response, status=400)
            if (
                User.objects.filter(personnel_number=personnel_number)
                .exclude(personnel_number=instance.personnel_number)
                .exists()
            ):
                response = {
                    "success": False,
                    "message": "Personnel number already exists.",
                }
                return Response(response, status=400)
            departments = Department.objects.filter(department_id=department_id)
            if not departments.exists():
                response = {
                    "success": False,
                    "message": "Department not found",
                }
                return Response(response, status=400)

            with transaction.atomic():
                instance.full_name = full_name
                instance.email = email
                instance.phone_number = phone_number
                instance.personnel_number = personnel_number
                instance.role = role
                instance.department = departments.first()
                instance.is_download_drawing = is_download_drawing
                instance.is_view_layout = is_view_layout
                instance.is_view_manual = is_view_manual
                instance.is_view_standard = is_view_standard
                instance.is_disable_dwg_file = is_disable_dwg_file
                instance.designation = designation
                instance.is_view_technical_calculation = is_view_technical_calculation
                instance.is_design_user = is_design_user
                instance.save()
                response = {
                    "success": True,
                    "message": "User updated  successfully.",
                    "results": UserDetailSerializer(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UserStatusUpadteApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = UserDetailSerializer

    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            user_id = data.get("id", None)
            user_status = data.get("status", "ACTIVE") == "ACTIVE"
            if not user_id:
                response = {"success": False, "message": "Required used ID"}
                return Response(response, status=400)
            try:
                user = User.objects.get(id=user_id, is_superuser=False)
            except User.DoesNotExist:
                response = {"success": False, "message": "User doesn't exist."}
                return Response(response, status=400)
            if not user_status:
                user.jti_token = None
            user.is_active = user_status
            user.save()
            response = {
                "success": True,
                "message": "User status updated successfully.",
                "results": self.serializer_class(user).data,
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UserChangePasswordApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class

    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            user_id = data.get("id", None)
            c_password = data.get("c_password", None)
            password = data.get("password", None)
            if not ([c_password, password, user_id]):
                response = {"success": False, "message": "All the mandatory fields are required"}
                return Response(response, status=400)
            try:
                user = User.objects.get(id=user_id, is_superuser=False)
            except User.DoesNotExist:
                response = {"success": False, "message": "User doesn't exist."}
                return Response(response, status=400)
            if c_password == password:
                user.set_password(password)
                if user.jti_token:
                    user.jti_token = None
                    device_info = parse_user_agent(request)
                    LogInOutLog.objects.create(
                        user=user,
                        message="Logout",
                        details="User Logout (change password)",
                        device_info=device_info,
                    )
                user.save()
                response = {
                    "success": True,
                    "message": "User password updated successfully.",
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Confirm Password not matched.",
                }
                return Response(response, status=400)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UserDrawingLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingLogListSerializer

    def get(self, request, user_id=None):
        try:
            # retrive single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)

            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(drawing__drawing_number__icontains=query)
                    | Q(drawing__drawing_type__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                DrawingLog.objects.select_related()
                .filter(filter_criteria)
                .order_by("-action_time")
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class UserStandardLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = StandardLogSerializer

    def get(self, request, user_id=None):
        try:
            # retrive single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)

            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(standard__standard_no__icontains=query)
                    | Q(standard__standard_type__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                StandardLog.objects.select_related('standard', 'user')
                .filter(filter_criteria)
                .order_by("-action_time")
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class UserManualLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = ManualLogSerializer

    def get(self, request, user_id=None):
        try:
            # retrive single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)

            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(manual__manual_no__icontains=query)
                    | Q(manual__manual_type__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                ManualLog.objects.select_related("manual", "user")
                .filter(filter_criteria)
                .order_by("-action_time")
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class UserSIRLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = SIRLogSerializer
    
    def get(self, request, user_id=None):
        try:
            # retrieve single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)
            
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(sir__sir_number__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                    | Q(details__icontains=query)
                )
            instance = (
                SIRLog.objects.select_related("sir", "user")
                .filter(filter_criteria)
                .order_by("-action_time")
            )
            
            # paginate the results using the custom pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        

class UserStabilityCertificateLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = StabilityCertificationLogSerializer
    
    def get(self, request, user_id=None):
        try:
            # retrive single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)

            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(stability_certification__certificate_number__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                StabilityCertificationLog.objects.select_related("stability_certification", "user")
                .filter(filter_criteria)
                .order_by("-action_time")
            )
            
            # paginate the results using the custom pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
    

class UserComplianceLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = ComplianceLogSerializer
    
    def get(self, request, user_id=None):
        try:
            # retrieve single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)
            
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(compliance__reference_number__icontains=query)
                    | Q(status__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                ComplianceLog.objects.select_related("compliance", "user")
                .filter(filter_criteria)
                .order_by("-action_time")
            )
            
            # paginate the results using the custom pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class UserLogInLogoutLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = UserLoginLogoutLogListSerializer

    def get(self, request, user_id=None):
        try:
            # retrive single object of user model
            if user_id:
                filter_criteria = Q(user__id=user_id)
            else:
                filter_criteria = Q(user__id=request.user.id)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(user__personnel_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(details__icontains=query)
                    | Q(message__icontains=query)
                )
            instance = (
                LogInOutLog.objects.select_related("user")
                .filter(filter_criteria)
                .order_by("-action_time")
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {"results": serializer.data, "count": instance.count()}, status=200
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DepartmentApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = DepartmentSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Department.objects.select_related()
                    .filter(
                        Q(name__icontains=query) | Q(department_id__icontains=query)
                    )
                    .order_by("name")
                )
            else:
                instance = Department.objects.all().order_by("name")

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response({"results": serializer.data}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                department_id = data.get("department_id", None)
                if not name and not department_id:
                    response = {
                        "success": False,
                        "message": "Required department name.",
                    }
                    return Response(response, status=400)

                if Department.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Department name already exists.",
                    }
                    return Response(response, status=400)
                if Department.objects.filter(department_id=department_id).exists():
                    response = {
                        "success": False,
                        "message": "Department id already exists.",
                    }
                    return Response(response, status=400)

                instance = Department.objects.create(
                    name=name, department_id=department_id
                )
                response = {
                    "success": True,
                    "message": "Department created  successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                dep_id = data.get("id", None)
                department_id = data.get("department_id", None)
                name = data.get("name", None)
                if not all([name, department_id, dep_id]):
                    response = {"success": False, "message": "Required all field."}
                    return Response(response, status=400)
                try:
                    instance = Department.objects.get(id=dep_id)
                except Department.DoesNotExist:
                    response = {"success": False, "message": "Department not found."}
                    return Response(response, status=400)
                if (
                    Department.objects.filter(name=name)
                    .exclude(name=instance.name)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Department already exists.",
                    }
                    return Response(response, status=400)
                if (
                    Department.objects.filter(department_id=department_id)
                    .exclude(department_id=instance.department_id)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Department id already exists.",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.department_id = department_id
                instance.save()
                response = {
                    "success": True,
                    "message": "Department updated successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def delete(self, request):
        try:
            if id := request.GET.get("id"):
                try:
                    department = Department.objects.get(id = id)
                except:
                    raise ValueError("Department Not found")
            else:
                raise ValueError("required Department ID")
            
            if replace_id := request.GET.get("replace_id"):
                try:
                    re_department = Department.objects.get(department_id = replace_id)
                except:
                    raise ValueError("Replaced Department Not found")
            else:
                raise ValueError("required replace Department ID")
            if department == re_department:
                raise ValueError("Choose different replace Department ID")
            Drawing.objects.filter(department= department).update(department = re_department)
            User.objects.filter(department = department).update(department = re_department)
            Manual.objects.filter(department= department).update(department = re_department)
            SIR.objects.filter(department= department).update(department = re_department)
            StabilityCertification.objects.filter(department= department).update(department = re_department)
            Compliance.objects.filter(department = department).update(department = re_department)
            department.delete()
            return Response({"message": "Department Deleted Successfully", "results": id}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class UnitApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = UnitSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Unit.objects.select_related()
                    .filter(Q(name__icontains=query) | Q(unit_id__icontains=query))
                    .order_by("name")
                )
            else:
                instance = Unit.objects.all().order_by("name")

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response({"results": serializer.data}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                unit_id = data.get("unit_id", None)
                if not name and not unit_id:
                    response = {
                        "success": False,
                        "message": "Required department name.",
                    }
                    return Response(response, status=400)

                if Unit.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Unit name already exists.",
                    }
                    return Response(response, status=400)
                if Unit.objects.filter(unit_id=unit_id).exists():
                    response = {
                        "success": False,
                        "message": "Unit id already exists.",
                    }
                    return Response(response, status=400)

                instance = Unit.objects.create(name=name, unit_id=unit_id)
                response = {
                    "success": True,
                    "message": "Unit created  successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                uni_id = data.get("id", None)
                unit_id = data.get("unit_id", None)
                name = data.get("name", None)
                if not all([name, unit_id, uni_id]):
                    response = {"success": False, "message": "Required all field."}
                    return Response(response, status=400)
                try:
                    instance = Unit.objects.get(id=uni_id)
                except Unit.DoesNotExist:
                    response = {"success": False, "message": "Unit not found."}
                    return Response(response, status=400)
                if Unit.objects.filter(name=name).exclude(name=instance.name).exists():
                    response = {
                        "success": False,
                        "message": "Unit already exists.",
                    }
                    return Response(response, status=400)
                if (
                    Unit.objects.filter(unit_id=unit_id)
                    .exclude(unit_id=instance.unit_id)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Unit id already exists.",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.unit_id = unit_id
                instance.save()
                response = {
                    "success": True,
                    "message": "Unit updated successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def delete(self, request):
        try:
            if id := request.GET.get("id"):
                try:
                    unit = Unit.objects.get(id = id)
                except:
                    raise ValueError("Unit Not found")
            else:
                raise ValueError("required Unit ID")
            
            if replace_id := request.GET.get("replace_id"):
                try:
                    re_unit = Unit.objects.get(unit_id = replace_id)
                except:
                    raise ValueError("Replaced Unit Not found")
            else:
                raise ValueError("required replace Unit ID")
            if unit == re_unit:
                raise ValueError("Choose different replace Unit ID")
            Drawing.objects.filter(unit= unit).update(unit = re_unit)
            Manual.objects.filter(unit= unit).update(unit = re_unit)
            SIR.objects.filter(unit= unit).update(unit = re_unit)
            StabilityCertification.objects.filter(unit= unit).update(unit = re_unit)
            Compliance.objects.filter(unit = unit).update(unit = re_unit)
            unit.delete()
            return Response({"message": "Unit Deleted Successfully", "results": id}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class RSVolumeApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = VolumeSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query", None):
                instance = Volume.objects.only('name').filter(name__icontains=query).order_by("volume_id")
            else:
                instance = Volume.objects.only('name').all().order_by("volume_id")

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response({"results": serializer.data}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                if not name:
                    response = {
                        "success": False,
                        "message": "Required name",
                    }
                    return Response(response, status=400)
                if Volume.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Volume name already exists.",
                    }
                    return Response(response, status=400)
                
                instance = Volume.objects.create(name=name)
                response = {
                    "success": True,
                    "message": "Volume created  successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                id = data.get("id", None)
                if not name and not id:
                    response = {
                        "success": False,
                        "message": "Required all field",
                    }
                    return Response(response, status=400)
                try:
                    volume = Volume.objects.get(id = id)
                except:
                    response = {
                        "success": False,
                        "message": "Volume not found",
                    }
                    return Response(response, status=400)
                
                volume.name=name
                volume.save()
                response = {
                    "success": True,
                    "message": "volume Updated  successfully.",
                    "results": self.serializer_class(volume).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def delete(self, request):
        try:
            if id := request.GET.get("id"):
                try:
                    volume = Volume.objects.get(id = id)
                except:
                    raise ValueError("Volume Not found")
            else:
                raise ValueError("required Volume ID")
            
            if replace_id := request.GET.get("replace_id"):
                try:
                    re_volume = Volume.objects.get(id = replace_id)
                except:
                    raise ValueError("Replaced Volume Not found")
            else:
                raise ValueError("required replace Volume ID")
            if volume == re_volume:
                raise ValueError("Choose different replace Volume ID")
            Subvolume.objects.filter(volume= volume).update(volume = re_volume)
            volume.delete()
            return Response({"message": "Volume Deleted Successfully", "results": id}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        

class RSSubVolumeApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = SubVolumeSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Subvolume.objects.select_related()
                    .filter(Q(name__icontains=query) | Q(volume__name__icontains = query)| Q(sub_volume_no__icontains = query))
                    .order_by("sub_volume_no")
                )
            else:
                instance = Subvolume.objects.all().order_by("sub_volume_no")

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response({"results": serializer.data}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                sub_volume_no = data.get("sub_volume_no", None)
                volume_id = data.get("volume_id", None)
                if not name and not sub_volume_no and not volume_id:
                    response = {
                        "success": False,
                        "message": "Required all field",
                    }
                    return Response(response, status=400)
                try:
                    volume = Volume.objects.get(id = volume_id)
                except:
                    response = {
                        "success": False,
                        "message": "Volume not found",
                    }
                    return Response(response, status=400)
                if Subvolume.objects.filter(name=name, volume=volume).exists():
                    response = {
                        "success": False,
                        "message": "Sub volume name already exists.",
                    }
                    return Response(response, status=400)
                if Subvolume.objects.filter(sub_volume_no=sub_volume_no, volume=volume).exists():
                    response = {
                        "success": False,
                        "message": "Sub volume no already exists.",
                    }
                    return Response(response, status=400)

                instance = Subvolume.objects.create(name=name, sub_volume_no=sub_volume_no, volume=volume)
                response = {
                    "success": True,
                    "message": "Sub volume created  successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                sub_volume_id = data.get("id", None)
                sub_volume_no = data.get("sub_volume_no", None)
                volume_id = data.get("volume_id", None)
                if not name and not sub_volume_no and not volume_id and not sub_volume_id:
                    response = {
                        "success": False,
                        "message": "Required all field",
                    }
                    return Response(response, status=400)
                try:
                    volume = Volume.objects.get(id = volume_id)
                except:
                    response = {
                        "success": False,
                        "message": "Volume not found",
                    }
                    return Response(response, status=400)
                try:
                    sub_volume = Subvolume.objects.get(id = sub_volume_id)
                except:
                    response = {
                        "success": False,
                        "message": "Sub Volume not found",
                    }
                    return Response(response, status=400)
                
                if Subvolume.objects.filter(name=name, volume=volume).exclude(name = sub_volume.name).exists():
                    response = {
                        "success": False,
                        "message": "Sub volume name already exists.",
                    }
                    return Response(response, status=400)
                if Subvolume.objects.filter(sub_volume_no=sub_volume_no, volume=volume).exclude(sub_volume_no=sub_volume.sub_volume_no).exists():
                    response = {
                        "success": False,
                        "message": "Sub volume no already exists.",
                    }
                    return Response(response, status=400)

                sub_volume.name=name 
                sub_volume.sub_volume_no=sub_volume_no
                sub_volume.volume=volume
                sub_volume.save()
                response = {
                    "success": True,
                    "message": "Sub volume Updated  successfully.",
                    "results": self.serializer_class(sub_volume).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_admin_user
    def delete(self, request):
        try:
            if id := request.GET.get("id"):
                try:
                    sub_volume = Subvolume.objects.get(id = id)
                except:
                    raise ValueError("Sub-Volume Not found")
            else:
                raise ValueError("required Sub-Volume ID")
            
            if replace_id := request.GET.get("replace_id"):
                try:
                    re_sub_volume = Subvolume.objects.get(id = replace_id)
                except:
                    raise ValueError("Replaced Sub-Volume Not found")
            else:
                raise ValueError("required replace Sub-volume ID")
            if sub_volume == re_sub_volume:
                raise ValueError("Choose different replace Sub-volume ID")
            Drawing.objects.filter(sub_volume= sub_volume).update(sub_volume = re_sub_volume)
            sub_volume.delete()
            return Response({"message": "Sub-Volume Deleted Successfully", "results": id}, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
# all search related api for dropdown


class SearchUnitApiView(APIView):
    serializer_class = SearchUnitSerializer

    def get(self, request, id=None):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name__icontains=query) | Q(unit_id__icontains=query)
                )
            exclude_id = request.GET.get("exclude_id", None)
            if exclude_id:
                instance = Unit.objects.filter(filter_criteria).exclude(id = exclude_id).order_by("name")
            else:
                instance = Unit.objects.filter(filter_criteria).order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Unit Search List",
                "results":serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchDepartmentApiView(APIView):
    serializer_class = SearchDepartmentSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name__icontains=query) | Q(department_id__icontains=query)
                )
            exclude_id = request.GET.get("exclude_id", None)
            if exclude_id:    
                instance = Department.objects.filter(filter_criteria).exclude(id = exclude_id).order_by("name")
            else:
                instance = Department.objects.filter(filter_criteria).order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Department Search List",
                "results":serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchSubVolumeApiView(APIView):
    serializer_class = SearchVolumeSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name__icontains=query) | Q(sub_volume_no__icontains=query)
                )
            exclude_id = request.GET.get("exclude_id")
            if exclude_id:
                instance = Subvolume.objects.filter(filter_criteria).exclude(id = exclude_id).order_by("sub_volume_no", "name")
            else:
                instance = Subvolume.objects.filter(filter_criteria).order_by("sub_volume_no", "name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Volume Search List",
                "results":serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchRSVolumeApiView(APIView):
    serializer_class = SearchRSVolumeSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name__icontains=query) | Q(volume_id__icontains=query)
                )
            exclude_id = request.GET.get("exclude_id")
            if exclude_id:
                instance = Volume.objects.filter(filter_criteria).exclude(id= exclude_id).order_by("name")
            else:
                instance = Volume.objects.filter(filter_criteria).order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Volume Search List",
                "results":serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)



class SearchUserApiView(APIView):
    serializer_class = SearchUserSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(full_name__icontains=query) | Q(personnel_number__icontains=query)
                )
            instance = User.objects.filter(filter_criteria).order_by("full_name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Unit Search List",
                "results":serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
