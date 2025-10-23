import re
from django.db import transaction
from .serializers import EmployeeSerializer, AutomationJobSerializer,PowerLabJobSerializer,RepairLabJobSerializer, EmployeeSearchSerializer, WeighingMaintenanceJobSerializer, WeighingOperationJobSerializer,CCTVJobSerializer,EmployeeTableSearchSerializer,SlideImageSerializer,ScreenerSlidesSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .pagination import CustomPagination
from .models import AutomationJob,PowerLabJob,RepairLabJob, LAB_STATUS_CHOICES,WeighingMaintenanceJob,WeighingOperationJob,SHIFT_TYPE_CHOICE,CCTVJob,SlideImage
from django.db.models import Q, Count, F
from AuthApp.utils import ExceptionDetails
from datetime import datetime, timedelta, date
from calendar import monthrange
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models.functions import TruncDate
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator 
from django.utils import timezone
import os
# <-- Add this import
# Define logger
logger = logging.getLogger(__name__)

# views.py

class AutomationJobView(APIView, CustomPagination):
    serializer_class = AutomationJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = AutomationJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Automation Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()
            
            if query := request.GET.get("query"):
                filter_criteria &= (
                    Q(department__icontains=query) |
                    Q(area__icontains=query) |
                    Q(job_description__icontains=query) |
                    Q(action_taken__icontains=query) |
                    Q(remarks__icontains=query)
                )

            if department := request.GET.get("department"):
                filter_criteria &= Q(department__iexact=department)
            
            if area := request.GET.get("area"):
                filter_criteria &= Q(area=area)

            if start_date := request.GET.get("start_date"):
                filter_criteria &= Q(job_start_time__date__gte=start_date)

            if end_date := request.GET.get("end_date"):
                filter_criteria &= Q(job_completion_time__date__lte=end_date)

            instance = (
                AutomationJob.objects.select_related("entry_by", "modify_by")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Automation Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            validation_response = self._validate_data(data)
            if validation_response:
                return validation_response

            with transaction.atomic():
                instance = AutomationJob.objects.create(
                    entry_by=request.user,
                    department=data["department"],
                    area=data["area"],
                    job_description=data["job_description"],
                    job_start_time=data["job_start_time"],
                    job_completion_time=data["job_completion_time"],
                    action_taken=data["action_taken"],
                    remarks=data.get("remarks", ""),
                    persons=data["persons"],
                )

                return Response({
                    "success": True,
                    "message": "Automation Job Created Successfully",
                    "data": self.serializer_class(instance).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data):
        required_fields = [
            "department", "area", "job_description", 
            "job_start_time", "job_completion_time",
            "action_taken", "persons"
        ]
        
        if missing := [f for f in required_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        datetime_format = "%Y-%m-%dT%H:%M"
        now = datetime.now()

        try:
            job_start_time = datetime.strptime(data["job_start_time"], datetime_format)
        except ValueError:
            return self._error("Invalid job start datetime format. Expected format: YYYY-MM-DDTHH:MM")

        try:
            job_completion_time = datetime.strptime(data["job_completion_time"], datetime_format)
        except ValueError:
            return self._error("Invalid job completion datetime format. Expected format: YYYY-MM-DDTHH:MM")

        if job_start_time > now :
            return self._error("Job start  time cannot be in the future")

        if job_completion_time <= job_start_time:
            return self._error("Job completion time must be later than job start time")

        return None
    
    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = AutomationJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser or creator
            if not user.is_superuser and instance.entry_by != user:
                return self._error("You are not authorized to update this job", status=403)

            validation_response = self._validate_data(data)
            if validation_response:
                return validation_response

            with transaction.atomic():
                update_fields = [
                    "department", "area", "job_description",
                    "job_start_time", "job_completion_time",
                    "action_taken", "remarks", "persons"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "Automation Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except AutomationJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def patch(self, request, id=None):
        """
        Partial update of an AutomationJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = AutomationJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate datetime fields if provided
            datetime_format = "%Y-%m-%dT%H:%M"
            now = datetime.now()

            if "job_start_time" in data:
                try:
                    job_start_time = datetime.strptime(data["job_start_time"], datetime_format)
                    if job_start_time > now:
                        return self._error("Job start time cannot be in the future")
                except ValueError:
                    return self._error("Invalid job start datetime format. Expected format: YYYY-MM-DDTHH:MM")

            if "job_completion_time" in data:
                try:
                    job_completion_time = datetime.strptime(data["job_completion_time"], datetime_format)
                    if job_completion_time > now:
                        return self._error("Job completion time cannot be in the future")
                except ValueError:
                    return self._error("Invalid job completion datetime format. Expected format: YYYY-MM-DDTHH:MM")

            # Validate time sequence if both times are provided
            if "job_start_time" in data and "job_completion_time" in data:
                if job_completion_time <= job_start_time:
                    return self._error("Job completion time must be later than job start time")

            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "department", "area", "job_description",
                    "job_start_time", "job_completion_time",
                    "action_taken", "remarks", "persons"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                instance.modify_by = request.user
                instance.save()
                
                return Response({
                    "success": True,
                    "message": "Automation Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except AutomationJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)
   
class InProgressPowerLabJobView(APIView):
    serializer_class = PowerLabJobSerializer
    
    def get(self, request):
        try:
            filter_criteria = Q(is_save_draft=False, status="In Progress")
            instance = (
                PowerLabJob.objects.select_related("assigned_staff", "entry_by", "modify_by").prefetch_related("present_staffs").filter(filter_criteria)
                .order_by("created_at")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Inprogress Power Lab Jobs List Get Successfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)  
        
class PowerLabJobView(APIView, CustomPagination):
    serializer_class = PowerLabJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = PowerLabJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Power Lab Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()
            
            # Filter for in-progress jobs
            if request.GET.get("in_progress") == "true":
                filter_criteria &= Q(status="In Progress")
            
            # Add draft filtering if requested
            is_draft = request.GET.get("is_draft")

            if is_draft == "true":
                # Show only drafts created by the logged-in user
                filter_criteria &= Q(is_save_draft=True, entry_by=request.user)
            elif is_draft == "false":
                # Show only finalized jobs (non-drafts)
                filter_criteria &= Q(is_save_draft=False)
            else:
                # Show both finalized jobs and user's own drafts
                filter_criteria &= Q(
                    Q(is_save_draft=False) | Q(is_save_draft=True, entry_by=request.user)
                )
            
            if query := request.GET.get("query"):
                filter_criteria &= Q(work_order_number__icontains=query)

            if shift := request.GET.get("shift"):
                filter_criteria &= Q(shift=shift)
                
            if status := request.GET.get("status"):
                filter_criteria &= Q(status=status)    
            
            if date := request.GET.get("date"):
                filter_criteria &= Q(date=date)

            instance = (
                PowerLabJob.objects.select_related("assigned_staff", "entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Power Lab Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            present_staffs_instance = User.objects.filter(id__in=data["present_staffs"], area__name__icontains="Power Labs")
            
            validation_response = self._validate_data(data, present_staffs_instance)
            if validation_response:
                return validation_response

            with transaction.atomic():
                created_jobs = [self._create_job(data, job, request.user, present_staffs_instance) for job in data["jobs"]]

                if inprogress_jobs := data.get('inprogress_job', []):
                    for job in inprogress_jobs:
                        self._update_inprogress_job(job, request.user)

                return Response({
                    "success": True,
                    "message": f"{len(created_jobs)} Power Lab Job(s) Created Successfully",
                    "data": self.serializer_class(created_jobs, many=True).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data, present_staffs_instance):
        required_default_fields = ["date", "shift", "present_staffs"]
        if missing := [f for f in required_default_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        if not data.get("jobs") or not isinstance(data["jobs"], list):
            return self._error("At least one job entry is required")

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["date"]):
            return self._error("Invalid date format. Expected format: YYYY-MM-DD")

        default_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if default_date > datetime.now().date():
            return self._error("Date cannot be in the future")

        for i, job in enumerate(data["jobs"]):
            error = self._validate_job(job, i, present_staffs_instance)
            if error:
                return error

        if inprogress_jobs := data.get("inprogress_job", []):
            for i, job in enumerate(inprogress_jobs):
                error = self._validate_job(job, i, present_staffs_instance, in_progress=True)
                if error:
                    return error

        return None

    def _validate_job(self, job, index, present_staffs_instance, in_progress=False):
        required_fields = [
            "id" if in_progress else None,
            "department", 
            "work_order_number", 
            "assigned_staff", 
            "job_description",
            "action_taken", 
            "status",
            "remarks"
        ]
        required_fields = [f for f in required_fields if f]  # remove None

        if missing := [f for f in required_fields if not job.get(f)]:
            return self._error(
                f"{'In progress ' if in_progress else ''}Job {index+1} missing required fields: {', '.join(missing)}"
            )

        # Date validation only if fields are provided
        date_fields = [
            "work_order_receive_date", 
            "work_order_completion_date", 
            "information_given_department_date", 
            "material_handover_department_date"
        ]
        
        for field in date_fields:
            if job.get(field) and not re.match(r'^\d{4}-\d{2}-\d{2}$', job[field]):
                return self._error(
                    f"{'In progress ' if in_progress else ''}Job {index+1}: Invalid {field.replace('_', ' ')} format. Expected format: YYYY-MM-DD"
                )

        # Validate completion date only if both dates are provided and status is not "In Progress"
        if job.get("work_order_receive_date") and job.get("work_order_completion_date"):
            if job["status"] != "In Progress":  # Only validate if not In Progress
                receive_date = datetime.strptime(job["work_order_receive_date"], "%Y-%m-%d").date()
                completion_date = datetime.strptime(job["work_order_completion_date"], "%Y-%m-%d").date()
                now = datetime.now().date()

                if completion_date < receive_date:
                    return self._error(f"{'In progress ' if in_progress else ''}Job {index+1}: Completion date cannot be before receive date")
                if receive_date > now:
                    return self._error(f"{'In progress ' if in_progress else ''}Job {index+1}: Receive date cannot be in the future")

        valid_statuses = [s[0] for s in LAB_STATUS_CHOICES if not (in_progress and s[0] == "In Progress")]
        if job["status"] not in valid_statuses:
            return self._error(
                f"{'In progress ' if in_progress else ''}Job {index+1}: Invalid status. Expected one of {', '.join(valid_statuses)}"
            )

        if in_progress:
            try:
                existing = PowerLabJob.objects.get(id=job["id"], status="In Progress")
                if job["assigned_staff"] not in existing.present_staffs.values_list("id", flat=True):
                    return self._error(f"In progress Job {index+1}: Assigned staff must be among present staffs")
            except PowerLabJob.DoesNotExist:
                return self._error(f"In progress Job {index+1}: Job not found or already completed")
        else:
            if job["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                return Response({
                    "success": False,
                    "message": f"Job {index+1}: Invalid assigned staff. Expected one of the present staffs"
                }, status=400)

        return None

    def _create_job(self, data, job, user, present_staffs_instance):
        # Handle null dates for In Progress status
        completion_date = None if job["status"] == "In Progress" else job.get("work_order_completion_date")
        material_handover_date = None if job["status"] == "In Progress" else job.get("material_handover_department_date")

        instance = PowerLabJob.objects.create(
            entry_by=user,
            date=data["date"],
            shift=data["shift"],
            work_order_number=job["work_order_number"],
            work_order_receive_date=job.get("work_order_receive_date"),
            work_order_completion_date=completion_date,
            department=job["department"],
            assigned_staff=User.objects.get(id=job["assigned_staff"]),
            job_description=job["job_description"],
            action_taken=job["action_taken"],
            remarks=job.get("remarks", ""),
            information_given_department_date=job.get("information_given_department_date"),
            material_handover_department_date=material_handover_date,
            status=job["status"],
            is_save_draft=data.get("is_save_draft", False),
        )
        instance.present_staffs.set(present_staffs_instance)
        return instance

    def _update_inprogress_job(self, job, user):
        instance = PowerLabJob.objects.get(id=job["id"], status="In Progress")
        
        # Don't update completion dates if status is changing to In Progress
        if job.get("status") == "In Progress":
            job["work_order_completion_date"] = None
            job["material_handover_department_date"] = None

        for field in [
            "work_order_number", 
            "work_order_receive_date", 
            "work_order_completion_date",
            "department", 
            "job_description", 
            "action_taken", 
            "remarks",
            "information_given_department_date", 
            "material_handover_department_date", 
            "status"
        ]:
            setattr(instance, field, job.get(field, getattr(instance, field)))

        instance.assigned_staff = User.objects.get(id=job["assigned_staff"])
        instance.is_save_draft = False
        instance.modify_by = user
        instance.save()

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)
    # Update the put method in PowerLabJobView
    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = PowerLabJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser, creator, or area incharge
            is_area_incharge = hasattr(user, "area") and "Power Labs" in user.area['name']
            if not user.is_superuser and instance.entry_by != user and not is_area_incharge:
                return self._error("You are not authorized to update this job", status=403)

            # Validate present staffs if provided
            present_staffs = data.get("present_staffs", [])
            present_staffs_instance = User.objects.filter(
            id__in=present_staffs,
            area__name__icontains="Power Labs"
            )

            # Validate assigned staff is among present staffs
            assigned_staff_id = data.get("assigned_staff")
            if assigned_staff_id:
                try:
                    assigned_staff = User.objects.get(id=assigned_staff_id)
                    if assigned_staff.id not in [staff.id for staff in present_staffs_instance]:
                        return self._error("Assigned staff must be among present staffs", status=400)
                except User.DoesNotExist:
                    return self._error(f"Assigned staff with ID {assigned_staff_id} does not exist", status=400)

            # Date validations
            if data.get("work_order_receive_date") and data.get("work_order_completion_date"):
                if data["work_order_completion_date"] < data["work_order_receive_date"]:
                    return self._error("Completion date cannot be before receive date", status=400)


            with transaction.atomic():
                update_fields = [
                    "date", "shift", "work_order_number", "work_order_receive_date",
                    "work_order_completion_date", "department", "job_description",
                    "action_taken", "remarks", "information_given_department_date",
                    "material_handover_department_date", "status", "is_save_draft"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                if "assigned_staff" in data:
                    instance.assigned_staff = assigned_staff

                if present_staffs:
                    instance.present_staffs.set(present_staffs_instance)

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "Power Lab Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except PowerLabJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)



    def patch(self, request, id=None):
        """
        Partial update of a PowerLabJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = PowerLabJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate present staffs if provided
            if "present_staffs" in data:
                present_staffs_instance = User.objects.filter(
                    id__in=data["present_staffs"], 
                    area__name__icontains="Power Labs"
                )
                
                # Validate assigned staff is among present staffs if both are provided
                if "assigned_staff" in data and data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                    return self._error("Assigned staff must be among present staffs", status=400)
            
            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "date", "shift", "work_order_number", "work_order_receive_date",
                    "work_order_completion_date", "department", "job_description",
                    "action_taken", "remarks", "information_given_department_date",
                    "material_handover_department_date", "status", "is_save_draft"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                if "assigned_staff" in data:
                    instance.assigned_staff = User.objects.get(id=data["assigned_staff"])
                
                instance.modify_by = request.user
                instance.save()
                
                if "present_staffs" in data:
                    instance.present_staffs.set(present_staffs_instance)
                
                return Response({
                    "success": True,
                    "message": "Power Lab Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except PowerLabJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

class InProgressRepairLabJobView(APIView):
    serializer_class = RepairLabJobSerializer
    
    def get(self, request):
        try:
            filter_criteria = Q(is_save_draft=False, status="In Progress")
            instance = (
                RepairLabJob.objects.select_related("assigned_staff", "entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("created_at")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Inprogress Repair Lab Jobs List Get Successfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class  RepairLabJobView(APIView, CustomPagination):
    serializer_class = RepairLabJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = RepairLabJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Repair Lab Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()
            
            # Filter for in-progress jobs
            if request.GET.get("in_progress") == "true":
                filter_criteria &= Q(status="In Progress")
            
            # Add draft filtering logic
            is_draft = request.GET.get("is_draft")

            if is_draft == "true":
                # Show only drafts created by the logged-in user
                filter_criteria &= Q(is_save_draft=True, entry_by=request.user)
            elif is_draft == "false":
                # Show only finalized jobs (non-drafts)
                filter_criteria &= Q(is_save_draft=False)
            else:
                # Show both finalized jobs and user's own drafts
                filter_criteria &= Q(
                    Q(is_save_draft=False) | Q(is_save_draft=True, entry_by=request.user)
                )

            
            if query := request.GET.get("query"):
                filter_criteria &= Q(work_order_number__icontains=query)

            if shift := request.GET.get("shift"):
                filter_criteria &= Q(shift=shift)
                
            if status := request.GET.get("status"):
                filter_criteria &= Q(status=status)    
            
            if date := request.GET.get("date"):
                filter_criteria &= Q(date=date)

            instance = (
                RepairLabJob.objects.select_related("assigned_staff", "entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Repair Lab Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            present_staffs_instance = User.objects.filter(id__in=data["present_staffs"], area__name__icontains="Repair Labs")
            
            validation_response = self._validate_data(data, present_staffs_instance)
            if validation_response:
                return validation_response

            with transaction.atomic():
                created_jobs = [self._create_job(data, job, request.user, present_staffs_instance) for job in data["jobs"]]

                if inprogress_jobs := data.get('inprogress_job', []):
                    for job in inprogress_jobs:
                        self._update_inprogress_job(job, request.user)

                return Response({
                    "success": True,
                    "message": f"{len(created_jobs)} Repair Lab Job(s) Created Successfully",
                    "data": self.serializer_class(created_jobs, many=True).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data, present_staffs_instance):
        required_default_fields = ["date", "shift", "present_staffs"]
        if missing := [f for f in required_default_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        if not data.get("jobs") or not isinstance(data["jobs"], list):
            return self._error("At least one job entry is required")

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["date"]):
            return self._error("Invalid date format. Expected format: YYYY-MM-DD")

        default_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if default_date > datetime.now().date():
            return self._error("Date cannot be in the future")

        for i, job in enumerate(data["jobs"]):
            error = self._validate_job(job, i, present_staffs_instance)
            if error:
                return error

        if inprogress_jobs := data.get("inprogress_job", []):
            for i, job in enumerate(inprogress_jobs):
                error = self._validate_job(job, i, present_staffs_instance, in_progress=True)
                if error:
                    return error

        return None

    def _validate_job(self, job, index, present_staffs_instance, in_progress=False):
        required_fields = [
            "id" if in_progress else None,
            "department", 
            "work_order_number", 
            "assigned_staff", 
            "job_description",
            "action_taken", 
            "status",
            "remarks"
        ]
        required_fields = [f for f in required_fields if f]  # remove None

        if missing := [f for f in required_fields if not job.get(f)]:
            return self._error(
                f"{'In progress ' if in_progress else ''}Job {index+1} missing required fields: {', '.join(missing)}"
            )

        # Date validation only if fields are provided
        date_fields = [
            "work_order_receive_date", 
            "work_order_completion_date", 
            "information_given_department_date", 
            "material_handover_department_date"
        ]
        
        for field in date_fields:
            if job.get(field) and not re.match(r'^\d{4}-\d{2}-\d{2}$', job[field]):
                return self._error(
                    f"{'In progress ' if in_progress else ''}Job {index+1}: Invalid {field.replace('_', ' ')} format. Expected format: YYYY-MM-DD"
                )

        # Validate completion date only if both dates are provided and status is not "In Progress"
        if job.get("work_order_receive_date") and job.get("work_order_completion_date"):
            if job["status"] != "In Progress":  # Only validate if not In Progress
                receive_date = datetime.strptime(job["work_order_receive_date"], "%Y-%m-%d").date()
                completion_date = datetime.strptime(job["work_order_completion_date"], "%Y-%m-%d").date()
                now = datetime.now().date()

                if completion_date < receive_date:
                    return self._error(f"{'In progress ' if in_progress else ''}Job {index+1}: Completion date cannot be before receive date")
                if receive_date > now:
                    return self._error(f"{'In progress ' if in_progress else ''}Job {index+1}: Receive date cannot be in the future")

        valid_statuses = [s[0] for s in LAB_STATUS_CHOICES if not (in_progress and s[0] == "In Progress")]
        if job["status"] not in valid_statuses:
            return self._error(
                f"{'In progress ' if in_progress else ''}Job {index+1}: Invalid status. Expected one of {', '.join(valid_statuses)}"
            )

        if in_progress:
            try:
                existing = RepairLabJob.objects.get(id=job["id"], status="In Progress")
                if job["assigned_staff"] not in [staff.id for staff in existing.present_staffs.all()]:
                    return self._error(f"In progress Job {index+1}: Assigned staff must be among present staffs")
            except RepairLabJob.DoesNotExist:
                return self._error(f"In progress Job {index+1}: Job not found or already completed")
        else:
            if job["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                return self._error(f"Job {index+1}: Assigned staff must be among present staffs")

        return None

    def _create_job(self, data, job, user, present_staffs_instance):
        # Handle date fields - convert empty strings to None
        date_fields = [
            'work_order_receive_date',
            'work_order_completion_date',
            'information_given_department_date',
            'material_handover_department_date'
        ]
        
        job_data = {
            'entry_by': user,
            'date': data["date"],
            'shift': data["shift"],
            'work_order_number': job["work_order_number"],
            'department': job["department"],
            'assigned_staff': User.objects.get(id=job["assigned_staff"]),
            'job_description': job["job_description"],
            'action_taken': job["action_taken"],
            'remarks': job.get("remarks", ""),
            'status': job["status"],
            'is_save_draft': data.get("is_save_draft", False),
        }
        
        # Add date fields if they exist
        for field in date_fields:
            if job.get(field):
                job_data[field] = job[field]
            else:
                job_data[field] = None

        # Clear completion dates if status is "In Progress"
        if job["status"] == "In Progress":
            job_data['work_order_completion_date'] = None
            job_data['material_handover_department_date'] = None

        instance = RepairLabJob.objects.create(**job_data)
        instance.present_staffs.set(present_staffs_instance)
        return instance

    def _update_inprogress_job(self, job, user):
        instance = RepairLabJob.objects.get(id=job["id"], status="In Progress")
        
        # Update fields
        fields_to_update = [
            "work_order_number", "department", "job_description", 
            "action_taken", "remarks", "status"
        ]
        
        for field in fields_to_update:
            setattr(instance, field, job.get(field, getattr(instance, field)))

        # Update staff
        instance.assigned_staff = User.objects.get(id=job["assigned_staff"])
        
        # Handle date fields
        date_fields = [
            'work_order_receive_date',
            'work_order_completion_date',
            'information_given_department_date',
            'material_handover_department_date'
        ]
        
        for field in date_fields:
            if job.get(field):
                setattr(instance, field, job[field])
            elif field in job:  # Explicit None/empty string passed
                setattr(instance, field, None)
        
        # Clear completion dates if status is "In Progress"
        if instance.status == "In Progress":
            instance.work_order_completion_date = None
            instance.material_handover_department_date = None
            
        instance.is_save_draft = False
        instance.modify_by = user
        instance.save()

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)

    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = RepairLabJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser, creator, or area incharge
            is_area_incharge = hasattr(user, "area") and "Repair Labs" in user.area['name']
            if not user.is_superuser and instance.entry_by != user and not is_area_incharge:
                return self._error("You are not authorized to update this job", status=403)

            # Validate present staffs if provided
            present_staffs = data.get("present_staffs", [])
            present_staffs_instance = User.objects.filter(
                id__in=present_staffs,
                area__name__icontains="Repair Labs"
            )

            # Validate assigned staff is among present staffs
            assigned_staff_id = data.get("assigned_staff")
            if assigned_staff_id:
                try:
                    assigned_staff = User.objects.get(id=assigned_staff_id)
                    if assigned_staff.id not in [staff.id for staff in present_staffs_instance]:
                        return self._error("Assigned staff must be among present staffs", status=400)
                except User.DoesNotExist:
                    return self._error(f"Assigned staff with ID {assigned_staff_id} does not exist", status=400)

            # Date validations
            if data.get("work_order_receive_date") and data.get("work_order_completion_date"):
                if data["work_order_completion_date"] < data["work_order_receive_date"]:
                    return self._error("Completion date cannot be before receive date", status=400)


            with transaction.atomic():
                update_fields = [
                    "date", "shift", "work_order_number", "work_order_receive_date",
                    "work_order_completion_date", "department", "job_description",
                    "action_taken", "remarks", "information_given_department_date",
                    "material_handover_department_date", "status", "is_save_draft"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                if "assigned_staff" in data:
                    instance.assigned_staff = assigned_staff

                if present_staffs:
                    instance.present_staffs.set(present_staffs_instance)

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "Repair Lab Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except RepairLabJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def patch(self, request, id=None):
        """
        Partial update of a RepairLabJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = RepairLabJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate present staffs if provided
            if "present_staffs" in data:
                present_staffs_instance = User.objects.filter(
                    id__in=data["present_staffs"], 
                    area__name__icontains="Repair Labs"
                )
                
                # Validate assigned staff is among present staffs if both are provided
                if "assigned_staff" in data and data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                    return self._error("Assigned staff must be among present staffs", status=400)
            
            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "date", "shift", "work_order_number", "work_order_receive_date",
                    "work_order_completion_date", "department", "job_description",
                    "action_taken", "remarks", "information_given_department_date",
                    "material_handover_department_date", "status", "is_save_draft"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                if "assigned_staff" in data:
                    instance.assigned_staff = User.objects.get(id=data["assigned_staff"])
                
                instance.modify_by = request.user
                instance.save()
                
                if "present_staffs" in data:
                    instance.present_staffs.set(present_staffs_instance)
                
                return Response({
                    "success": True,
                    "message": "Repair Lab Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except RepairLabJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)   

class WeighingMaintenanceJobView(APIView, CustomPagination):
    serializer_class = WeighingMaintenanceJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = WeighingMaintenanceJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Weighing Maintenance Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()

            if query := request.GET.get("query"):
                filter_criteria &= (
                    Q(complaint_nature__icontains=query) |
                    Q(reported_by__icontains=query) |
                    Q(remarks__icontains=query)
                )

            if complaint_nature := request.GET.get("complaint_nature"):
                filter_criteria &= Q(complaint_nature=complaint_nature)

            if shift := request.GET.get("shift"):
                filter_criteria &= Q(shift=shift)

            if date := request.GET.get("date"):
                filter_criteria &= Q(date=date)

            if weighbridge_location := request.GET.get("weighbridge_location"):
                filter_criteria &= Q(weighbridge_location=weighbridge_location)

            instance = (
                WeighingMaintenanceJob.objects.select_related("assigned_staff", "entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Weighing Maintenance Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            # Ensure present_staffs is a list of IDs
            present_staffs = data.get("present_staffs", [])
            if not isinstance(present_staffs, list):
                return self._error("present_staffs must be an array")
                
            present_staffs_instance = User.objects.filter(id__in=present_staffs)
            
            # Debug logging
            
            validation_response = self._validate_data(data, present_staffs_instance)
            if validation_response:
                return validation_response

            with transaction.atomic():
                instance = WeighingMaintenanceJob.objects.create(
                    entry_by=request.user,
                    date=data["date"],
                    shift=data["shift"],
                    complaint_time=data["complaint_time"],
                    complaint_nature=data["complaint_nature"],
                    weighbridge_location=data["weighbridge_location"],
                    reported_by=data["reported_by"],
                    action_taken=data["action_taken"],
                    remarks=data.get("remarks", ""),
                    assigned_staff_id=data["assigned_staff"],
                )
                instance.present_staffs.set(present_staffs_instance)

                return Response({
                    "success": True,
                    "message": "Weighing Maintenance Job Created Successfully",
                    "data": self.serializer_class(instance).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data, present_staffs_instance):
        required_fields = [
            "date", "shift", "complaint_time", "complaint_nature",
            "weighbridge_location", "reported_by", "action_taken",
            "present_staffs", "assigned_staff"
        ]
        
        if missing := [f for f in required_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["date"]):
            return self._error("Invalid date format. Expected format: YYYY-MM-DD")

        try:
            complaint_time = datetime.strptime(data["complaint_time"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self._error("Invalid complaint_time format. Expected format: YYYY-MM-DD HH:MM:SS")

        current_date = datetime.now().date()
        if datetime.strptime(data["date"], "%Y-%m-%d").date() > current_date:
            return self._error("Date cannot be in the future")

        if complaint_time.date() > current_date:
            return self._error("Complaint time cannot be in the future")

        if data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
            return self._error("Assigned staff must be among present staffs")

        

        if data["shift"] not in [choice[0] for choice in SHIFT_TYPE_CHOICE]:
            return self._error("Invalid shift type")

        return None

    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = WeighingMaintenanceJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser or creator
            is_area_incharge = hasattr(user, "area") and "Weighing Maintenance" in user.area['name']

            if not user.is_superuser and instance.entry_by != user and not is_area_incharge:
                return self._error("You are not authorized to update this job", status=403)

            # Validate present staffs if provided
            present_staffs = data.get("present_staffs", [])
            present_staffs_instance = User.objects.filter(
                id__in=present_staffs,
                area__name__icontains="Weighing Maintenance"
            )

            # Validate assigned staff is among present staffs
            assigned_staff_id = data.get("assigned_staff")
            if assigned_staff_id:
                try:
                    assigned_staff = User.objects.get(id=assigned_staff_id)
                    if assigned_staff.id not in [staff.id for staff in present_staffs_instance]:
                        return self._error("Assigned staff must be among present staffs", status=400)
                except User.DoesNotExist:
                    return self._error(f"Assigned staff with ID {assigned_staff_id} does not exist", status=400)

            with transaction.atomic():
                update_fields = [
                    "date", "shift", "complaint_time", "complaint_nature",
                    "weighbridge_location", "reported_by", "action_taken",
                    "remarks"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                if "assigned_staff" in data:
                    instance.assigned_staff = assigned_staff

                if present_staffs:
                    instance.present_staffs.set(present_staffs_instance)

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "Weighing Maintenance Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except WeighingMaintenanceJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def patch(self, request, id=None):
        """
        Partial update of a WeighingMaintenanceJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = WeighingMaintenanceJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate present staffs if provided
            if "present_staffs" in data:
                present_staffs_instance = User.objects.filter(id__in=data["present_staffs"])
                
                # Validate assigned staff is among present staffs if both are provided
                if "assigned_staff" in data and data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                    return self._error("Assigned staff must be among present staffs", status=400)
            
            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "date", "shift", "complaint_time", "complaint_nature",
                    "weighbridge_location", "reported_by", "action_taken",
                    "remarks"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                if "assigned_staff" in data:
                    instance.assigned_staff = User.objects.get(id=data["assigned_staff"])
                
                instance.modify_by = request.user
                instance.save()
                
                if "present_staffs" in data:
                    instance.present_staffs.set(present_staffs_instance)
                
                return Response({
                    "success": True,
                    "message": "Weighing Maintenance Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except WeighingMaintenanceJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)

class WeighingOperationJobView(APIView, CustomPagination):
    serializer_class = WeighingOperationJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = WeighingOperationJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Weighing Operation Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()
            
            if query := request.GET.get("query"):
                filter_criteria &= (
                    Q(source__icontains=query) |
                    Q(commodity__icontains=query) |
                    Q(wb_register_number__icontains=query) |
                    Q(rake__icontains=query) |
                    Q(general__icontains=query)
                )

            if shift := request.GET.get("shift"):
                filter_criteria &= Q(shift=shift)
            
            if date := request.GET.get("date"):
                filter_criteria &= Q(date=date)

            if source := request.GET.get("source"):
                filter_criteria &= Q(source=source)

            if commodity := request.GET.get("commodity"):
                filter_criteria &= Q(commodity=commodity)

            instance = (
                WeighingOperationJob.objects.select_related("assigned_staff", "entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Weighing Operation Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            # Ensure present_staffs is a list of IDs
            present_staffs = data.get("present_staffs", [])
            if not isinstance(present_staffs, list):
                return self._error("present_staffs must be an array")
                
            present_staffs_instance = User.objects.filter(id__in=present_staffs)
            
            # Debug logging
            
            validation_response = self._validate_data(data, present_staffs_instance)
            if validation_response:
                return validation_response

            with transaction.atomic():
                instance = WeighingOperationJob.objects.create(
                    entry_by=request.user,
                    date=data["date"],
                    shift=data["shift"],
                    source=data["source"],
                    commodity=data["commodity"],
                    wb_register_number=data["wb_register_number"],
                    rake=data["rake"],
                    number_of_wagon=data["number_of_wagon"],
                    gross_weight=data["gross_weight"],
                    net_weight=data["net_weight"],
                    rake_in_time=data["rake_in_time"],
                    system_one=data.get("system_one", ""),
                    system_two=data.get("system_two", ""),
                    general=data.get("general", ""),
                    assigned_staff_id=data["assigned_staff"],
                )
                instance.present_staffs.set(present_staffs_instance)

                return Response({
                    "success": True,
                    "message": "Weighing Operation Job Created Successfully",
                    "data": self.serializer_class(instance).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data, present_staffs_instance):
        required_fields = [
            "date", "shift", "source", "commodity", "wb_register_number",
            "rake", "number_of_wagon", "gross_weight", "net_weight",
            "rake_in_time", "present_staffs", "assigned_staff"
        ]
        
        if missing := [f for f in required_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["date"]):
            return self._error("Invalid date format. Expected format: YYYY-MM-DD")

        try:
            rake_in_time = datetime.strptime(data["rake_in_time"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self._error("Invalid rake_in_time format. Expected format: YYYY-MM-DD HH:MM:SS")

        current_date = datetime.now().date()
        if datetime.strptime(data["date"], "%Y-%m-%d").date() > current_date:
            return self._error("Date cannot be in the future")

        

        if data["shift"] not in [choice[0] for choice in SHIFT_TYPE_CHOICE]:
            return self._error("Invalid shift type")

        if data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
            return self._error("Assigned staff must be among present staffs")

        return None

    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = WeighingOperationJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser or creator
            is_area_incharge = hasattr(user, "area") and "Weighing Operation" in user.area['name']

            if not user.is_superuser and instance.entry_by != user and not is_area_incharge:
                return self._error("You are not authorized to update this job", status=403)

            # Validate present staffs if provided
            present_staffs = data.get("present_staffs", [])
            present_staffs_instance = User.objects.filter(
                id__in=present_staffs,
                area__name__icontains="Weighing Operation"
            )

            # Validate assigned staff is among present staffs
            assigned_staff_id = data.get("assigned_staff")
            if assigned_staff_id:
                try:
                    assigned_staff = User.objects.get(id=assigned_staff_id)
                    if assigned_staff.id not in [staff.id for staff in present_staffs_instance]:
                        return self._error("Assigned staff must be among present staffs", status=400)
                except User.DoesNotExist:
                    return self._error(f"Assigned staff with ID {assigned_staff_id} does not exist", status=400)

            with transaction.atomic():
                update_fields = [
                    "date", "shift", "source", "commodity", "wb_register_number",
                    "rake", "number_of_wagon", "gross_weight", "net_weight",
                    "rake_in_time", "system_one", "system_two", "general"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                if "assigned_staff" in data:
                    instance.assigned_staff = assigned_staff

                if present_staffs:
                    instance.present_staffs.set(present_staffs_instance)

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "Weighing Operation Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except WeighingOperationJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def patch(self, request, id=None):
        """
        Partial update of a WeighingOperationJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = WeighingOperationJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate present staffs if provided
            if "present_staffs" in data:
                present_staffs_instance = User.objects.filter(id__in=data["present_staffs"])
                
                # Validate assigned staff is among present staffs if both are provided
                if "assigned_staff" in data and data["assigned_staff"] not in [staff.id for staff in present_staffs_instance]:
                    return self._error("Assigned staff must be among present staffs", status=400)
            
            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "date", "shift", "source", "commodity", "wb_register_number",
                    "rake", "number_of_wagon", "gross_weight", "net_weight",
                    "rake_in_time", "system_one", "system_two", "general"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                if "assigned_staff" in data:
                    instance.assigned_staff = User.objects.get(id=data["assigned_staff"])
                
                instance.modify_by = request.user
                instance.save()
                
                if "present_staffs" in data:
                    instance.present_staffs.set(present_staffs_instance)
                
                return Response({
                    "success": True,
                    "message": "Weighing Operation Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except WeighingOperationJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)
       
class CCTVJobView(APIView, CustomPagination):
    serializer_class = CCTVJobSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = CCTVJob.objects.get(id=id)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "CCTV Job Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            filter_criteria = Q()
            
            if query := request.GET.get("query"):
                filter_criteria &= (
                    Q(complain_nature__icontains=query) |
                    Q(supporting_staff__icontains=query) |
                    Q(complain_site__icontains=query) |
                    Q(remarks__icontains=query)
                )

            if shift := request.GET.get("shift"):
                filter_criteria &= Q(shift=shift)
            
            if date := request.GET.get("date"):
                filter_criteria &= Q(date=date)

            if job_type := request.GET.get("job_type"):
                filter_criteria &= Q(complain_nature=job_type)

            instance = (
                CCTVJob.objects.select_related("entry_by", "modify_by")
                .prefetch_related("present_staffs")
                .filter(filter_criteria)
                .order_by("-created_at")
            )

            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "CCTV Jobs List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            
            if not isinstance(data, dict):
                return self._error("Data must be an object")

            # Ensure present_staffs is a list of IDs
            present_staffs = data.get("present_staffs", [])
            if not isinstance(present_staffs, list):
                return self._error("present_staffs must be an array")
                
            present_staffs_instance = User.objects.filter(id__in=present_staffs)
            
            validation_response = self._validate_data(data, present_staffs_instance)
            if validation_response:
                return validation_response

            with transaction.atomic():
                instance = CCTVJob.objects.create(
                    entry_by=request.user,
                    date=data["date"],
                    shift=data["shift"],
                    supporting_staff=data["supporting_staff"],
                    complain_site=data["complain_site"],
                    complain_received_time=data["complain_received_time"],
                    complain_nature=data["complain_nature"],
                    complain_details=data["complain_details"],
                    action_taken=data["action_taken"],
                    completion_time=data.get("completion_time"),
                    remarks=data.get("remarks", ""),
                )
                instance.present_staffs.set(present_staffs_instance)

                return Response({
                    "success": True,
                    "message": "CCTV Job Created Successfully",
                    "data": self.serializer_class(instance).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _validate_data(self, data, present_staffs_instance):
        required_fields = [
            "date", "shift", "supporting_staff", "complain_site",
            "complain_received_time", "complain_nature", "complain_details",
            "action_taken", "present_staffs"
        ]
        
        if missing := [f for f in required_fields if not data.get(f)]:
            return self._error(f"Missing required fields: {', '.join(missing)}")

        if not re.match(r'^\d{4}-\d{2}-\d{2}$', data["date"]):
            return self._error("Invalid date format. Expected format: YYYY-MM-DD")

        try:
            complain_received_time = datetime.strptime(data["complain_received_time"], "%Y-%m-%d %H:%M:%S")
            if "completion_time" in data and data["completion_time"]:
                completion_time = datetime.strptime(data["completion_time"], "%Y-%m-%d %H:%M:%S")
                if completion_time < complain_received_time:
                    return self._error("Completion time cannot be before complaint received time")
        except ValueError:
            return self._error("Invalid time format. Expected format: YYYY-MM-DD HH:MM:SS")

        current_date = datetime.now().date()
        if datetime.strptime(data["date"], "%Y-%m-%d").date() > current_date:
            return self._error("Date cannot be in the future")

        

        if data["shift"] not in [choice[0] for choice in SHIFT_TYPE_CHOICE]:
            return self._error("Invalid shift type")

        return None

    def put(self, request, id=None):
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)

            data = request.data
            instance = CCTVJob.objects.get(id=id)

            user = request.user

            # Check permissions: superuser or creator
            if not user.is_superuser and instance.entry_by != user:
                return self._error("You are not authorized to update this job", status=403)

            # Validate present staffs if provided
            present_staffs = data.get("present_staffs", [])
            present_staffs_instance = User.objects.filter(id__in=present_staffs)

            with transaction.atomic():
                update_fields = [
                    "date", "shift", "supporting_staff", "complain_site",
                    "complain_received_time", "complain_nature", "complain_details",
                    "action_taken", "completion_time", "remarks"
                ]

                for field in update_fields:
                    if field in data:
                        setattr(instance, field, data[field])

                if present_staffs:
                    instance.present_staffs.set(present_staffs_instance)

                instance.modify_by = user
                instance.save()

                return Response({
                    "success": True,
                    "message": "CCTV Job updated successfully",
                    "data": self.serializer_class(instance).data
                }, status=200)

        except CCTVJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def patch(self, request, id=None):
        """
        Partial update of a CCTVJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Job ID is required for update", status=400)
            
            data = request.data
            instance = CCTVJob.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not request.user.is_superuser and instance.entry_by != request.user:
                return self._error("You can only update jobs you created", status=403)
            
            # Validate present staffs if provided
            if "present_staffs" in data:
                present_staffs_instance = User.objects.filter(id__in=data["present_staffs"])
            
            # Update the instance with provided fields only
            with transaction.atomic():
                fields_to_update = [
                    "date", "shift", "supporting_staff", "complain_site",
                    "complain_received_time", "complain_nature", "complain_details",
                    "action_taken", "completion_time", "remarks"
                ]
                
                for field in fields_to_update:
                    if field in data:
                        setattr(instance, field, data[field])
                
                instance.modify_by = request.user
                instance.save()
                
                if "present_staffs" in data:
                    instance.present_staffs.set(present_staffs_instance)
                
                return Response({
                    "success": True,
                    "message": "CCTV Job updated successfully",
                    "data": self.serializer_class(instance).data
                })
                
        except CCTVJob.DoesNotExist:
            return self._error("Job not found", status=404)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)    

class EmployeesView(APIView, CustomPagination):
    serializer_class = EmployeeSerializer
    def get_permission_level(self, user):
        role = user.role.lower().strip()
        if role == 'admin':
            return 'admin'
        elif role == 'area incharge':
            return 'area incharge'
        elif role == 'shift incharge':
            return 'shift incharge'
        elif role == 'executive':
            return 'executive'
        return None



    def get(self, request, id=None):
        try:
            if id:
                # Single employee view
                instance = User.objects.filter(id=id, is_superuser=False).first()
                if not instance:
                    response = {"success": False, "message": "Employee not found"}
                    return Response(response, status=404)
                
                # Permission checks
                permission_level = self.get_permission_level(request.user)

                if permission_level == 'admin':
                    pass  # Admin can view any employee
                elif permission_level == 'area incharge':
                    # Area Incharge can only view employees in their areas
                    user_areas = self._normalize_areas(request.user.area)
                    instance_areas = self._normalize_areas(instance.area)
                    if not set(instance_areas).intersection(user_areas):
                        response = {"success": False, "message": "Not allowed to view this employee"}
                        return Response(response, status=403)
                elif permission_level in ['shift incharge', 'executive']:
                    # Shift Incharges and Executives can only view active employees
                    if not instance.is_active:
                        response = {"success": False, "message": "Not allowed to view this employee"}
                        return Response(response, status=403)
                else:
                    # Other users can't view individual employees
                    response = {"success": False, "message": "Not allowed to view individual employees"}
                    return Response(response, status=403)
                
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Employee Get Successfully",
                    "data": serializer.data,
                }
                return Response(response, status=200)
            
            # List view
            filter_criteria = Q(is_superuser=False)
            
            # Handle area filtering for Area Incharge and Shift Incharge
            if request.user.role.lower() in ['area incharge', 'shift incharge']:
                user_areas = self._normalize_areas(request.user.area)
                if user_areas:
                    # Create OR conditions for each area
                    area_query = Q()
                    for area in user_areas:
                        # Use JSON field query for area.name if area is stored as JSON
                        area_query |= Q(area__name__icontains=area) | Q(area__name__iexact=area)
                    filter_criteria &= area_query
                else:
                    # If no areas assigned, return empty list for non-admins
                    if not request.user.is_superuser:
                        return Response({
                            "success": True,
                            "message": "Employee List Get Successfully",
                            "data": [],
                            "total": 0,
                        }, status=200)
            
            # Search functionality
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name__icontains=query) | 
                    Q(personnel_number__icontains=query) |
                    Q(role__icontains=query)
                )
            
            # Status filter if provided
            if status := request.GET.get("status"):
                filter_criteria &= Q(is_active=(status.lower() == "active"))
            
            if role := request.GET.get("role"):
                filter_criteria &= Q(role=role)
            
            if area := request.GET.get("area"):
                filter_criteria &= Q(area__name__icontains=[area])
            
            if sort_by := request.GET.get("sort_by", "-created_at"):
                sort_by_list = ["personnel_number", "name", "-created"]
                if sort_by not in sort_by_list:
                    sort_by = "-created_at"
            else:
                sort_by = "-created_at"
            


            # Ordering and pagination
            instance = User.objects.filter(filter_criteria).order_by(sort_by)
            page = self.paginate_queryset(instance, request, view=self)
            serializer = self.serializer_class(page, many=True)
            result = self.get_paginated_response(serializer.data)
            
            response = {
                "success": True,
                "message": "Employee List Get Successfully",
                "data": result.data["results"],
                "total": result.data["count"],
            }
            return Response(response, status=200)
            
        except Exception as e:
            logger.error(f"Error in Employee get: {str(e)}")
            response = {"success": False, "message": "An error occurred while processing your request"}
            return Response(response, status=500)

    def _normalize_areas(self, area_data):
        """Helper method to normalize area data into a list of strings"""
        if not area_data:
            return []
        
        # Handle case where area_data is a dictionary with 'name' key
        if isinstance(area_data, dict) and 'name' in area_data:
            name_data = area_data['name']
            if isinstance(name_data, list):
                return [str(area).strip().lower() for area in name_data if area]
            elif isinstance(name_data, str):
                return [name.strip().lower() for name in name_data.split(',') if name.strip()]
        
        # Handle case where area_data is already a list or string
        if isinstance(area_data, list):
            return [str(area).strip().lower() for area in area_data if area]
        elif isinstance(area_data, str):
            return [area.strip().lower() for area in area_data.split(',') if area.strip()]
        
        return []

    def post(self, request):
        try:
            # Validate user permissions first
            if not request.user.is_authenticated:
                return Response(
                    {"success": False, "message": "Authentication required"}, 
                    status=401
                )
            
            # Only admin and area incharges can create employees
            if request.user.role not in ['Admin', 'Area Incharge']:
                return Response(
                    {"success": False, "message": "User not authorized to create employees"}, 
                    status=403
                )
            
            with transaction.atomic():
                data = request.data
                
                # Required fields validation
                required_fields = ['name', 'personnel_number', 'role', 'password']
                if not all(field in data for field in required_fields):
                    return Response(
                        {"success": False, "message": f"Missing required fields: {', '.join(required_fields)}"},
                        status=400
                    )
                
                name = data['name'].strip()
                personnel_number = data['personnel_number'].strip()
                role = data['role'].strip()
                areas = data.get('area', [])  # Now expecting a list of areas
                password = data['password']

                # Validate personnel number format
                if not personnel_number.isdigit():
                    return Response(
                        {"success": False, "message": "Personnel number must be numeric"},
                        status=400
                    )

                # Role validation
                valid_roles = ['Admin', 'Area Incharge', 'Shift Incharge', 'Executive']
                if role not in valid_roles:
                    return Response(
                        {"success": False, "message": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                        status=400
                    )

                # Area validation
                if role in ["Area Incharge", "Shift Incharge"] and not areas:
                    return Response(
                        {"success": False, "message": "At least one area is required for this role"},
                        status=400
                    )

                # For Shift Incharge, ensure exactly one area is selected
                if role == "Shift Incharge" and len(areas) != 1:
                    return Response(
                        {"success": False, "message": "Shift Incharge must have exactly one area"},
                        status=400
                    )

                # Permission-based validations
                if request.user.role == 'Area Incharge':
                    # Area Incharge can only create Shift Incharge
                    if role != 'Shift Incharge':
                        return Response(
                            {"success": False, "message": "You can only create Shift Incharge employees"},
                            status=403
                        )
                    
                    # Get user's areas properly
                    user_areas = request.user.area.get('name', [])
                    if not isinstance(user_areas, list):
                        user_areas = [user_areas]
                    
                    # Check if all selected areas are in user's areas
                    if not all(area in user_areas for area in areas):
                        return Response(
                            {"success": False, "message": f"You can only assign your areas ({', '.join(user_areas)})"},
                            status=403
                        )

                # Role-specific area restrictions
                if role == 'Admin' and areas:
                    return Response(
                        {"success": False, "message": "Admin cannot be assigned to any area"},
                        status=400
                    )

                if role == 'Shift Incharge' and 'Automation' in areas:
                    return Response(
                        {"success": False, "message": "Shift Incharge cannot be assigned to Automation area"},
                        status=400
                    )

                if 'Automation' in areas and role != 'Area Incharge':
                    return Response(
                        {"success": False, "message": "Automation area can only be assigned to Area Incharge"},
                        status=400
                    )

                # Check for existing personnel number
                if User.objects.filter(personnel_number=personnel_number).exists():
                    return Response(
                        {"success": False, "message": "Personnel number already exists"},
                        status=400
                    )

                # Create the user
                instance = User.objects.create_user(
                    name=name,
                    personnel_number=personnel_number,
                    role=role,
                    area={"name": areas},  # Now passing a list of areas
                    password=password,
                    is_active=True,
                    is_superuser=False
                )

                return Response(
                    {
                        "success": True,
                        "message": "User created successfully",
                        "data": self.serializer_class(instance).data
                    },
                    status=201
                )

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "message": "An error occurred while creating user"},
                status=500
            )

    def put(self, request, id):
        try:
            # Get the user instance to be updated
            instance = User.objects.get(id=id)
            
            # Determine permission level (make sure this method exists)
            permission_level = self.get_permission_level(request.user)
            
            # ========== PERMISSION CHECKS ==========
            if permission_level == 'admin':
                pass  # Admin can edit anything
            elif permission_level == 'area incharge':
                # Area Incharge can only edit employees in their areas and with lower roles
                user_areas = request.user.area.get('name', [])
                if not isinstance(user_areas, list):
                    user_areas = [user_areas]
                    
                instance_areas = instance.area.get('name', [])
                if not isinstance(instance_areas, list):
                    instance_areas = [instance_areas]
                    
                # Check if any area overlaps
                if not any(area in user_areas for area in instance_areas):
                    return Response(
                        {"success": False, "message": "Can only edit employees in your areas"},
                        status=403
                    )
                if instance.role.lower() in ['admin', 'executive']:
                    return Response(
                        {"success": False, "message": "Cannot edit this role"},
                        status=403
                    )
            elif permission_level == 'executive':
                # Executives can edit all employees except admins and area incharges
                if instance.role.lower() in ['admin', 'area incharge']:
                    return Response(
                        {"success": False, "message": "Cannot edit this role"},
                        status=403
                    )
            elif permission_level == 'shift incharge':
                # Shift Incharges can only edit employees in their areas with shift roles
                user_areas = request.user.area.get('name', [])
                if not isinstance(user_areas, list):
                    user_areas = [user_areas]
                    
                instance_areas = instance.area.get('name', [])
                if not isinstance(instance_areas, list):
                    instance_areas = [instance_areas]
                    
                if not any(area in user_areas for area in instance_areas):
                    return Response(
                        {"success": False, "message": "Can only edit employees in your areas"},
                        status=403
                    )
                if instance.role.lower() != 'shift incharge':
                    return Response(
                        {"success": False, "message": "Can only edit shift incharges"},
                        status=403
                    )
            else:
                return Response(
                    {"success": False, "message": "You don't have edit permissions"},
                    status=403
                )

            # ========== DATA VALIDATION ==========
            data = request.data
            required_fields = ['name', 'personnel_number', 'role']
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return Response(
                    {"success": False, "message": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=400
                )

            # Role validation
            new_role = data.get('role', '').lower()
            valid_roles = ['admin', 'area incharge', 'shift incharge', 'executive']
            if new_role not in valid_roles:
                return Response(
                    {"success": False, "message": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                    status=400
                )

            # Area validation
            areas = data.get('area', [])
            if not isinstance(areas, list):
                return Response(
                    {"success": False, "message": "Areas must be provided as a list"},
                    status=400
                )

            # Role-specific area restrictions
            if new_role == 'admin' and areas:
                return Response(
                    {"success": False, "message": "Admin cannot be assigned to any area"},
                    status=400
                )

            if new_role == 'shift incharge' and 'Automation' in areas:
                return Response(
                    {"success": False, "message": "Shift Incharge cannot be assigned to Automation area"},
                    status=400
                )

            # ========== UPDATE OPERATION ==========
            update_fields = []
            
            # Update basic fields
            instance.name = data['name']
            instance.personnel_number = data['personnel_number']
            instance.role = data['role']
            update_fields.extend(['name', 'personnel_number', 'role'])
            
            # Handle status
            status = data.get('status', 'active').lower()
            if status not in ['active', 'inactive']:
                return Response(
                    {"success": False, "message": "Status must be either 'Active' or 'Inactive'"},
                    status=400
                )
            instance.is_active = status == 'active'
            update_fields.append('is_active')
            
            # Handle areas - store as {'name': [area1, area2]}
            if new_role != 'admin':  # Admin doesn't need areas
                instance.area = {'name': areas}
                update_fields.append('area')
            
            # Save the updates
            instance.save(update_fields=update_fields)
            
            return Response({
                "success": True,
                "message": "User updated successfully",
                "data": self.serializer_class(instance).data
            }, status=200)
            
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=404
            )
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "message": f"An error occurred while updating user: {str(e)}"},
                status=500
            )
                    

    def delete(self, request, id):
        if request.user.is_superuser is False:
            response = {"success": False, "message": "User not allowed"}
            return Response(response, status=400)
        try:
            with transaction.atomic():
                instance = User.objects.filter(id=id, is_superuser=False).first()
                if instance:
                    instance.delete()
                    response = {
                        "success": True,
                        "message": "User Deleted Successfully",
                    }
                    return Response(response, status=200)
                response = {
                    "success": False,
                    "message": f"User Not Found with This ID {id}",
                }
                return Response(response, status=404)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
class EmployeesSearchView(APIView):
    serializer_class = EmployeeSearchSerializer

    def get(self, request, area=None):
        try:            
            if area is None:
                response = {"success": False, "message": "Employee not found"}
                return Response(response, status=404)
                
            instance = User.objects.filter(area__name__icontains=area).order_by("name")
            serializer_data = self.serializer_class(instance, many=True).data
            
            response = {
                "success": True,
                "message": "Employee List Get Successfully",
                "data": serializer_data,
            }
            return Response(response, status=200)
            
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": "An error occurred"}
            return Response(response, status=500)


class EmployeesSearchTableView(APIView):
    serializer_class = EmployeeTableSearchSerializer

    def get(self, request):
        try:
            search_query = request.query_params.get("search", "")
            if not search_query:
                return Response({"success": False, "message": "Search query required"}, status=400)

            queryset = User.objects.filter(
                Q(name__icontains=search_query) |
                Q(personnel_number__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(area__name__icontains=search_query) |
                Q(area__icontains=search_query)
            ).order_by("name").distinct()

            serializer = self.serializer_class(queryset, many=True)
            return Response({
                "success": True,
                "message": "Employee list fetched successfully",
                "data": serializer.data,
                "total": len(serializer.data),
            }, status=200)

        except Exception as e:
            return Response({"success": False, "message": "An error occurred"}, status=500)
        
class PasswordResetView(APIView):
    def put(self, request, id):
        try:
            # Get user and validate data
            target_user = User.objects.get(id=id)
            current_user = request.user
            data = request.data
            
            # Permission checks
            if not current_user.is_superuser:
                # Area incharge can only reset passwords for their area
                if current_user.role.lower() == 'area incharge':
                    if target_user.area != current_user.area:
                        return Response(
                            {"success": False, "message": "You can only reset passwords for your area", "code": "permission_denied"},
                            status=status.HTTP_403_FORBIDDEN
                        )
                # Shift incharge can only reset their own password
                elif current_user.role.lower() == 'shift incharge':
                    if target_user.id != current_user.id:
                        return Response(
                            {"success": False, "message": "You can only reset your own password", "code": "permission_denied"},
                            status=status.HTTP_403_FORBIDDEN
                        )
                # Regular users can only reset their own password
                elif target_user.id != current_user.id:
                    return Response(
                        {"success": False, "message": "You can only reset your own password", "code": "permission_denied"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Validate required fields
            if 'new_password' not in data:
                return Response(
                    {"success": False, "message": "New password is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For non-admin users changing their own password, require current password
            if not current_user.is_superuser and target_user.id == current_user.id:
                if 'current_password' not in data:
                    return Response(
                        {"success": False, "message": "Current password is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not target_user.check_password(data['current_password']):
                    return Response(
                        {
                            "success": False,
                            "message": "Current password is incorrect",
                            "code": "incorrect_password"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate new password complexity
            if len(data['new_password']) < 8:
                return Response(
                    {
                        "success": False,
                        "message": "Password must be at least 8 characters long",
                        "code": "password_too_short"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            target_user.set_password(data['new_password'])
            target_user.save()
            
            return Response({
                "success": True,
                "message": "Password has been updated successfully"
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User account not found",
                    "code": "user_not_found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred",
                    "code": "server_error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SiteWiseReportAPI(APIView):
    def get(self, request):
        sites = CCTVJob.objects.order_by('complain_site').values_list('complain_site', flat=True).distinct()
        return Response({'sites': list(sites)})

class JobNatureReportAPI(APIView):
    def get(self, request):
        natures = CCTVJob.objects.order_by('complain_nature').values_list('complain_nature', flat=True).distinct()
        return Response({'job_natures': list(natures)}) 
    
class RepairLabSummaryReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            lab_id = request.GET.get("lab_id")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = RepairLabJob.objects.filter(is_save_draft=False)

            if lab_id:
                qs = qs.filter(lab_id=lab_id)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            # Group by period and get counts
            periods = qs.values('date').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status="Completed")),
                taken_back=Count('id', filter=Q(status="Taken Back")),
                beyond_repair=Count('id', filter=Q(status="Beyond Repair"))
            ).order_by('date')

            # Prepare report data
            data = []
            for period in periods:
                total = period['total']
                completed = period['completed']
                taken_back = period['taken_back']
                beyond_repair = period['beyond_repair']
                
                pct = lambda x: round((x / total) * 100, 2) if total else 0.0

                data.append({
                    "date": period['date'].strftime("%Y-%m-%d"),
                    "total_job_received": total,
                    "total_completed": completed,
                    "total_taken_back": taken_back,
                    "total_beyond_repair": beyond_repair,
                    "percent_completed": pct(completed),
                    "percent_taken_back": pct(taken_back),
                    "percent_beyond_repair": pct(beyond_repair),
                    "percent_work_order_completed": pct(completed + taken_back + beyond_repair),
                })

            if export:
                return self.export_csv(
                    data,
                    [
                        "date", "total_job_received", "total_completed",
                        "total_taken_back", "total_beyond_repair",
                        "percent_completed", "percent_taken_back",
                        "percent_beyond_repair", "percent_work_order_completed"
                    ],
                    "repair_lab_summary_report.csv"
                )

            paginator = Paginator(data, page_size)
            page_obj = paginator.get_page(page)

            return Response({
                "success": True,
                "message": "Repair lab summary report",
                "data": list(page_obj),
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response


class RepairLabPersonReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        # Same implementation as in RepairLabSummaryReportAPIView
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            lab_id = request.GET.get("lab_id")
            person_id = request.GET.get("person_id")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = RepairLabJob.objects.filter(is_save_draft=False)

            if lab_id:
                qs = qs.filter(lab_id=lab_id)
            if person_id:
                qs = qs.filter(assigned_staff_id=person_id)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            # Get user data with counts
            user_data = qs.values(
                'date', 
                'assigned_staff__id',
                'assigned_staff__name'
            ).annotate(
                total_assigned=Count('id'),
                completed=Count('id', filter=Q(status="Completed")),
                taken_back=Count('id', filter=Q(status="Taken Back")),
                beyond_repair=Count('id', filter=Q(status="Beyond Repair"))
            ).order_by('date', 'assigned_staff__name')

            # Prepare report data
            data = []
            for entry in user_data:
                data.append({
                    "date": entry['date'].strftime("%Y-%m-%d"),
                    "person_name": entry['assigned_staff__name'],
                    "job_assigned": entry['total_assigned'],
                    "job_completed": entry['completed'],
                    "job_taken_back": entry['taken_back'],
                    "job_beyond_repair": entry['beyond_repair'],
                })

            if export:
                return self.export_csv(
                    data,
                    [
                        "date", "person_name",
                        "job_assigned", "job_completed",
                        "job_taken_back", "job_beyond_repair"
                    ],
                    "repair_lab_person_report.csv"
                )

            paginator = Paginator(data, page_size)
            page_obj = paginator.get_page(page)

            return Response({
                "success": True,
                "message": "Repair lab person report",
                "data": list(page_obj),
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response
              
              
class PowerLabSummaryReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            lab_id = request.GET.get("lab_id")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = PowerLabJob.objects.filter(is_save_draft=False)

            if lab_id:
                qs = qs.filter(lab_id=lab_id)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            # Group by period and get counts
            periods = qs.values('date').annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status="Completed")),
                taken_back=Count('id', filter=Q(status="Taken Back")),
                beyond_repair=Count('id', filter=Q(status="Beyond Repair"))
            ).order_by('date')

            # Prepare report data
            data = []
            for period in periods:
                total = period['total']
                completed = period['completed']
                taken_back = period['taken_back']
                beyond_repair = period['beyond_repair']
                
                pct = lambda x: round((x / total) * 100, 2) if total else 0.0

                data.append({
                    "date": period['date'].strftime("%Y-%m-%d"),
                    "total_job_received": total,
                    "total_completed": completed,
                    "total_taken_back": taken_back,
                    "total_beyond_repair": beyond_repair,
                    "percent_completed": pct(completed),
                    "percent_taken_back": pct(taken_back),
                    "percent_beyond_repair": pct(beyond_repair),
                    "percent_work_order_completed": pct(completed + taken_back + beyond_repair),
                })

            if export:
                return self.export_csv(
                    data,
                    [
                        "date", "total_job_received", "total_completed",
                        "total_taken_back", "total_beyond_repair",
                        "percent_completed", "percent_taken_back",
                        "percent_beyond_repair", "percent_work_order_completed"
                    ],
                    "power_lab_summary_report.csv"
                )

            paginator = Paginator(data, page_size)
            page_obj = paginator.get_page(page)

            return Response({
                "success": True,
                "message": "Power lab summary report",
                "data": list(page_obj),
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response


class PowerLabPersonReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            lab_id = request.GET.get("lab_id")
            person_id = request.GET.get("person_id")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = PowerLabJob.objects.filter(is_save_draft=False)

            if lab_id:
                qs = qs.filter(lab_id=lab_id)
            if person_id:
                qs = qs.filter(assigned_staff_id=person_id)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            # Get distinct users first to populate dropdown
            distinct_users = User.objects.filter(
                id__in=qs.values_list('assigned_staff', flat=True).distinct()
            ).values('id', 'name')

            # Get user data with counts
            user_data = qs.values(
                'date', 
                'assigned_staff__id',
                'assigned_staff__name'
            ).annotate(
                total_assigned=Count('id'),
                completed=Count('id', filter=Q(status="Completed")),
                taken_back=Count('id', filter=Q(status="Taken Back")),
                beyond_repair=Count('id', filter=Q(status="Beyond Repair"))
            ).order_by('date', 'assigned_staff__name')

            # Prepare report data
            data = []
            for entry in user_data:
                data.append({
                    "date": entry['date'].strftime("%Y-%m-%d"),
                    "person_name": entry['assigned_staff__name'],
                    "job_assigned": entry['total_assigned'],
                    "job_completed": entry['completed'],
                    "job_taken_back": entry['taken_back'],
                    "job_beyond_repair": entry['beyond_repair'],
                })

            if export:
                return self.export_csv(
                    data,
                    [
                        "date", "person_name",
                        "job_assigned", "job_completed",
                        "job_taken_back", "job_beyond_repair"
                    ],
                    "power_lab_person_report.csv"
                )

            paginator = Paginator(data, page_size)
            page_obj = paginator.get_page(page)

            return Response({
                "success": True,
                "message": "Power lab person report",
                "data": list(page_obj),
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response
              
class CCTVJobReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            shift = request.GET.get("shift")
            complain_site = request.GET.get("complain_site")
            complain_nature = request.GET.get("complain_nature")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = CCTVJob.objects.all()

            if shift:
                qs = qs.filter(shift__iexact=shift)
            if complain_site:
                qs = qs.filter(complain_site__icontains=complain_site)
            if complain_nature:
                qs = qs.filter(complain_nature__iexact=complain_nature)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            qs = qs.order_by("-complain_received_time")

            if export:
                data = list(qs.values(
                    'date', 'shift', 'supporting_staff', 'complain_site',
                    'complain_received_time', 'complain_nature', 'complain_details',
                    'action_taken', 'completion_time', 'remarks',
                    entry_by_name=F('entry_by__name'),
                    modify_by_name=F('modify_by__name')
                ))

                for item in data:
                    item['date'] = item['date'].strftime("%Y-%m-%d")
                    item['complain_received_time'] = item['complain_received_time'].strftime("%Y-%m-%d %H:%M:%S")
                    item['completion_time'] = item['completion_time'].strftime("%Y-%m-%d %H:%M:%S") if item['completion_time'] else ""

                return self.export_csv(
                    data,
                    ["date", "shift", "supporting_staff", "complain_site",
                     "complain_received_time", "complain_nature", "complain_details",
                     "action_taken", "completion_time", "remarks",
                     "entry_by_name", "modify_by_name"],
                    "cctv_job_report.csv"
                )

            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)

            serialized_data = []
            for job in page_obj:
                serialized_data.append({
                    "id": job.id,
                    "date": job.date.strftime("%Y-%m-%d"),
                    "shift": job.shift,
                    "supporting_staff": job.supporting_staff,
                    "complain_site": job.complain_site,
                    "complain_received_time": job.complain_received_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "complain_nature": job.complain_nature,
                    "complain_details": job.complain_details,
                    "action_taken": job.action_taken,
                    "completion_time": job.completion_time.strftime("%Y-%m-%d %H:%M:%S") if job.completion_time else None,
                    "remarks": job.remarks,
                    "entry_by": {"name": job.entry_by.name if job.entry_by else None},
                    "modify_by": {"name": job.modify_by.name if job.modify_by else None},
                    "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": job.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                })

            return Response({
                "success": True,
                "message": "Filtered CCTV jobs",
                "data": serialized_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response


class WeighingMaintenanceReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month_str = request.GET.get("month", "").strip().lower()
            year_str = request.GET.get("year", "").strip()
            month_name_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
                'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
                'nov': 11, 'november': 11, 'dec': 12, 'december': 12,
            }
            month = month_name_map.get(month_str)
            year = int(year_str) if year_str.isdigit() else today.year
            if not month:
                raise ValueError(f"Invalid month: {month_str}")
            start = date(year, month, 1)
            end = date(year + (1 if month == 12 else 0), (month % 12) + 1, 1) - timedelta(days=1)

        elif report_type == 'calendar_year':
            year_str = request.GET.get("year", "").strip()
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year_str = request.GET.get("year", "").strip()
            base_year = int(year_str) if year_str.isdigit() else (
                today.year if today.month >= 4 else today.year - 1
            )
            start = date(base_year, 4, 1)
            end = date(base_year + 1, 3, 31)

        elif report_type == 'custom':
            from_date = request.GET.get("from_date")
            to_date = request.GET.get("to_date")
            if not from_date or not to_date:
                return None, None
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end


    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            complaint_nature = request.GET.get("complaint_nature")
            weighbridge_location = request.GET.get("weighbridge_location")
            shift = request.GET.get("shift")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = WeighingMaintenanceJob.objects.all()

            if complaint_nature:
                qs = qs.filter(complaint_nature__iexact=complaint_nature)
            if weighbridge_location:
                qs = qs.filter(weighbridge_location__iexact=weighbridge_location)
            if shift:
                qs = qs.filter(shift__iexact=shift)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            qs = qs.order_by("-date")

            if export:
                data = list(qs.values(
                    'date', 'shift', 'complaint_nature', 'weighbridge_location',
                    'complaint_time', 'reported_by', 'action_taken', 'remarks',
                    assigned_staff_name=F('assigned_staff__name'),
                    entry_by_name=F('entry_by__name')
                ))

                for item in data:
                    item['date'] = item['date'].strftime("%Y-%m-%d")
                    item['complaint_time'] = item['complaint_time'].strftime("%Y-%m-%d %H:%M:%S") if item['complaint_time'] else ""

                return self.export_csv(
                    data,
                    ["date", "shift", "complaint_nature", "weighbridge_location",
                     "complaint_time", "reported_by", "action_taken", "remarks",
                     "assigned_staff_name", "entry_by_name"],
                    "weighing_maintenance_report.csv"
                )

            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)

            serialized_data = []
            for job in page_obj:
                serialized_data.append({
                    "id": job.id,
                    "date": job.date.strftime("%Y-%m-%d"),
                    "shift": job.shift,
                    "complaint_nature": job.complaint_nature,
                    "weighbridge_location": job.weighbridge_location,
                    "complaint_time": job.complaint_time.strftime("%Y-%m-%d %H:%M:%S") if job.complaint_time else None,
                    "reported_by": job.reported_by,
                    "action_taken": job.action_taken,
                    "remarks": job.remarks,
                    "assigned_staff": {"name": job.assigned_staff.name if job.assigned_staff else None},
                    "entry_by": {"name": job.entry_by.name if job.entry_by else None},
                    "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": job.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                })

            return Response({
                "success": True,
                "message": "Filtered weighing maintenance jobs",
                "data": serialized_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response  
class WeighingOperationReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            next_month = month % 12 + 1
            next_month_year = year + (1 if next_month == 1 else 0)
            end = date(next_month_year, next_month, 1) - timedelta(days=1)

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            shift = request.GET.get("shift")
            source = request.GET.get("source")
            commodity = request.GET.get("commodity")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = WeighingOperationJob.objects.all()

            if shift:
                qs = qs.filter(shift__iexact=shift)
            if source:
                qs = qs.filter(source__iexact=source)
            if commodity:
                qs = qs.filter(commodity__iexact=commodity)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(date__range=[start, end])

            qs = qs.order_by("-date")

            if export:
                data = list(qs.values(
                    'date', 'shift', 'source', 'commodity', 'wb_register_number', 'rake',
                    'number_of_wagon', 'gross_weight', 'net_weight', 'rake_in_time',
                    'system_one', 'system_two', 'general',
                    assigned_staff_name=F('assigned_staff__name'),
                    entry_by_name=F('entry_by__name')
                ))

                for item in data:
                    item['date'] = item['date'].strftime("%Y-%m-%d")
                    item['rake_in_time'] = item['rake_in_time'].strftime("%Y-%m-%d %H:%M:%S") if item['rake_in_time'] else ""

                return self.export_csv(
                    data,
                    ["date", "shift", "source", "commodity", "wb_register_number", "rake",
                     "number_of_wagon", "gross_weight", "net_weight", "rake_in_time",
                     "system_one", "system_two", "general",
                     "assigned_staff_name", "entry_by_name"],
                    "weighing_operation_report.csv"
                )

            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)

            serialized_data = []
            for job in page_obj:
                serialized_data.append({
                    "id": job.id,
                    "date": job.date.strftime("%Y-%m-%d"),
                    "shift": job.shift,
                    "source": job.source,
                    "commodity": job.commodity,
                    "wb_register_number": job.wb_register_number,
                    "rake": job.rake,
                    "number_of_wagon": job.number_of_wagon,
                    "gross_weight": job.gross_weight,
                    "net_weight": job.net_weight,
                    "rake_in_time": job.rake_in_time.strftime("%Y-%m-%d %H:%M:%S") if job.rake_in_time else None,
                    "system_one": job.system_one,
                    "system_two": job.system_two,
                    "general": job.general,
                    "assigned_staff": {"name": job.assigned_staff.name if job.assigned_staff else None},
                    "entry_by": {"name": job.entry_by.name if job.entry_by else None},
                    "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": job.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                })

            return Response({
                "success": True,
                "message": "Filtered weighing operation jobs",
                "data": serialized_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response 
    
class AutomationJobReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_period_range(self, report_type, request):
        today = date.today()

        month_str = request.GET.get("month", "").strip().lower()
        year_str = request.GET.get("year", "").strip()
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        month_name_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        if report_type == 'weekly':
            start = today - timedelta(days=6)
            end = today

        elif report_type == 'monthly':
            month = month_name_map.get(month_str, today.month)
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])

        elif report_type == 'calendar_year':
            year = int(year_str) if year_str.isdigit() else today.year
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        elif report_type == 'financial_year':
            year = int(year_str) if year_str.isdigit() else today.year
            if today.month >= 4:
                start = date(year, 4, 1)
                end = date(year + 1, 3, 31)
            else:
                start = date(year - 1, 4, 1)
                end = date(year, 3, 31)

        elif report_type == 'custom' and from_date and to_date:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        else:
            return None, None

        return start, end

    def get(self, request):
        try:
            filter_type = request.GET.get("filter", "weekly")
            department = request.GET.get("department")
            area = request.GET.get("area")
            export = request.GET.get("export", "false").lower() == "true"
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))

            qs = AutomationJob.objects.all()

            if department:
                qs = qs.filter(department__iexact=department)
            if area:
                qs = qs.filter(area__icontains=area)

            start, end = self.get_period_range(filter_type, request)
            if start and end:
                qs = qs.filter(job_start_time__date__range=[start, end])

            qs = qs.order_by("-job_start_time")

            if export:
                data = list(qs.values(
                    'department', 'area', 'job_start_time', 'job_completion_time',
                    'job_description', 'action_taken', 'remarks', 'persons',
                    entry_by_name=F('entry_by__name'),
                    modify_by_name=F('modify_by__name')
                ))

                for item in data:
                    item['job_start_time'] = item['job_start_time'].strftime("%Y-%m-%d %H:%M:%S")
                    item['job_completion_time'] = item['job_completion_time'].strftime("%Y-%m-%d %H:%M:%S") if item['job_completion_time'] else ""

                return self.export_csv(
                    data,
                    ["department", "area", "job_start_time", "job_completion_time",
                     "job_description", "action_taken", "remarks", "persons",
                     "entry_by_name", "modify_by_name"],
                    "automation_job_report.csv"
                )

            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)

            serialized_data = []
            for job in page_obj:
                serialized_data.append({
                    "id": job.id,
                    "department": job.department,
                    "area": job.area,
                    "job_start_time": job.job_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "job_completion_time": job.job_completion_time.strftime("%Y-%m-%d %H:%M:%S") if job.job_completion_time else None,
                    "job_description": job.job_description,
                    "action_taken": job.action_taken,
                    "remarks": job.remarks,
                    "persons": job.persons,
                    "entry_by": {"name": job.entry_by.name if job.entry_by else None},
                    "modify_by": {"name": job.modify_by.name if job.modify_by else None},
                    "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": job.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                })

            return Response({
                "success": True,
                "message": "Filtered automation jobs",
                "data": serialized_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def export_csv(self, data, fields, filename="export.csv"):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )
        response.write('\ufeff'.encode('utf-8'))  # Excel compatibility
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response
MODEL_MAP = {
    "automation": AutomationJob,
    "powerlab": PowerLabJob,
    "repairlab": RepairLabJob,
    "weighing_maintenance": WeighingMaintenanceJob,
    "weighing_operation": WeighingOperationJob,
    "cctv": CCTVJob,
}


class PowerLabJobStatusCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter_type = request.query_params.get("filter_type", "all").lower()
        today = timezone.now().date()

        # Calculate date range based on filter_type
        if filter_type == "weekly":
            start_date = today - timedelta(days=7)
        elif filter_type == "monthly":
            start_date = today.replace(day=1)
        elif filter_type == "yearly":
            start_date = today.replace(month=1, day=1)
        elif filter_type == "all":
            start_date = None
        else:
            return Response(
                {"error": "Invalid filter_type. Use 'weekly', 'monthly', 'yearly', or 'all'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter PowerLabJobs by date if not 'all'
        if start_date:
            jobs = PowerLabJob.objects.filter(date__gte=start_date)
        else:
            jobs = PowerLabJob.objects.all()

        # Count jobs grouped by status
        summary = (
            jobs.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        # Convert to dict with default 0 values for all status choices
        response_data = {label: 0 for label, _ in PowerLabJob._meta.get_field("status").choices}
        for item in summary:
            response_data[item["status"]] = item["count"]

        return Response(response_data, status=status.HTTP_200_OK)


class RepairLabJobStatusCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        filter_type = request.query_params.get("filter_type", "all").lower()
        today = timezone.now().date()

        # Calculate date range based on filter_type
        if filter_type == "weekly":
            start_date = today - timedelta(days=7)
        elif filter_type == "monthly":
            start_date = today.replace(day=1)
        elif filter_type == "yearly":
            start_date = today.replace(month=1, day=1)
        elif filter_type == "all":
            start_date = None
        else:
            return Response(
                {"error": "Invalid filter_type. Use 'weekly', 'monthly', 'yearly', or 'all'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter RepairLabJobs by date if not 'all'
        if start_date:
            jobs = RepairLabJob.objects.filter(date__gte=start_date)
        else:
            jobs = RepairLabJob.objects.all()

        # Count jobs grouped by status
        summary = (
            jobs.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        # Convert to dict with default 0 values for all status choices
        response_data = {label: 0 for label, _ in RepairLabJob._meta.get_field("status").choices}
        for item in summary:
            response_data[item["status"]] = item["count"]

        return Response(response_data, status=status.HTTP_200_OK) 


class JobCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        model_key = request.GET.get("model", None)

        today = timezone.now().date()

       


        try:
            if model_key:
                model_class = MODEL_MAP.get(model_key)
                if not model_class:
                    return Response({"error": "Invalid model name"}, status=400)
                count = model_class.objects.count()
                return Response({f"{model_key}_job_count": count}, status=200)

            # If no specific model requested, return all
            data = {
                "automation_job_count": AutomationJob.objects.count(),
                "power_lab_job_count": PowerLabJob.objects.count(),
                "repair_lab_job_count": RepairLabJob.objects.count(),
                "weighing_maintenance_job_count": WeighingMaintenanceJob.objects.count(),
                "weighing_operation_job_count": WeighingOperationJob.objects.count(),
                "cctv_job_count": CCTVJob.objects.count(),
            }
            return Response(data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)   
        
        
class MonthlyJobTrendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_type = request.GET.get("filter", "monthly").lower()
        today = timezone.now().date()

        if filter_type == "weekly":
            from_date = today - timedelta(days=7)
        elif filter_type == "monthly":
            from_date = today - timedelta(days=30)
        elif filter_type == "yearly":
            from_date = today.replace(month=1, day=1)
        elif filter_type == "all":
            from_date = None
        else:
            return Response(
                {"error": "Invalid filter_type. Use 'weekly', 'monthly', 'yearly', or 'all'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def get_job_data(model, label):
            queryset = model.objects
            if from_date:
                queryset = queryset.filter(created_at__date__gte=from_date)
            return (
                queryset
                .annotate(created_date=TruncDate("created_at"))
                .values("created_date")
                .annotate(count=Count("id"))
                .order_by("created_date")
            ), label

        models_data = [
            (AutomationJob, "Automation"),
            (PowerLabJob, "Power Lab"),
            (RepairLabJob, "Repair Lab"),
            (WeighingMaintenanceJob, "Weighing Maintenance"),
            (WeighingOperationJob, "Weighing Operation"),
            (CCTVJob, "CCTV"),
        ]

        result = {}
        all_dates = set()

        for model, label in models_data:
            queryset, label_name = get_job_data(model, label)
            date_dict = {}
            for entry in queryset:
                date_str = entry["created_date"].strftime("%Y-%m-%d")
                date_dict[date_str] = entry["count"]
                all_dates.add(date_str)
            result[label_name] = date_dict

        all_dates = sorted(list(all_dates))
        response_data = []

        for date in all_dates:
            row = {"date": date}
            for label in result:
                row[label] = result[label].get(date, 0)
            response_data.append(row)

        return Response(response_data)
    
    
class AllJobCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_type = request.GET.get("filter", "all").lower()
        today = timezone.now().date()

        if filter_type == "weekly":
            from_date = today - timedelta(days=7)
        elif filter_type == "monthly":
            from_date = today.replace(day=1)
        elif filter_type == "yearly":
            from_date = today.replace(month=1, day=1)
        elif filter_type == "all":
            from_date = None
        else:
            return Response(
                {"error": "Invalid filter_type. Use 'weekly', 'monthly', 'yearly', or 'all'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filters = {"created_at__date__gte": from_date} if from_date else {}

        automation_count = AutomationJob.objects.filter(**filters).count()
        powerlab_count = PowerLabJob.objects.filter(**filters).count()
        repairlab_count = RepairLabJob.objects.filter(**filters).count()
        weighing_maintenance_count = WeighingMaintenanceJob.objects.filter(**filters).count()
        weighing_operation_count = WeighingOperationJob.objects.filter(**filters).count()
        cctv_count = CCTVJob.objects.filter(**filters).count()

        total_count = (
            automation_count + powerlab_count + repairlab_count +
            weighing_maintenance_count + weighing_operation_count + cctv_count
        )

        return Response({
            "total_jobs": total_count,
            "automation_jobs": automation_count,
            "powerlab_jobs": powerlab_count,
            "repairlab_jobs": repairlab_count,
            "weighing_maintenance_jobs": weighing_maintenance_count,
            "weighing_operation_jobs": weighing_operation_count,
            "cctv_jobs": cctv_count
        }) 
        

class JobCountByShiftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_type = request.GET.get("filter", "all").lower()
        today = timezone.now().date()

        if filter_type == "weekly":
            from_date = today - timedelta(days=7)
        elif filter_type == "monthly":
            from_date = today.replace(day=1)
        elif filter_type == "yearly":
            from_date = today.replace(month=1, day=1)
        elif filter_type == "all":
            from_date = None
        else:
            return Response(
                {"error": "Invalid filter_type. Use 'weekly', 'monthly', 'yearly', or 'all'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shift_labels = [label for label, _ in SHIFT_TYPE_CHOICE]
        job_models = {
            "PowerLabJob": PowerLabJob,
            "RepairLabJob": RepairLabJob,
            "WeighingMaintenanceJob": WeighingMaintenanceJob,
            "WeighingOperationJob": WeighingOperationJob,
            "CCTVJob": CCTVJob,
        }

        response_data = {shift: {} for shift in shift_labels}
        total = 0

        for model_name, model in job_models.items():
            queryset = model.objects
            if from_date:
                queryset = queryset.filter(created_at__date__gte=from_date)
                
            shift_counts = queryset.values('shift').annotate(count=Count('id'))
            for entry in shift_counts:
                shift = entry['shift']
                count = entry['count']
                if shift in response_data:
                    response_data[shift][model_name] = count
                else:
                    response_data[shift] = {model_name: count}
                total += count

        response_data["total_jobs"] = total
        return Response(response_data)
    

class SlideImageAPIView(APIView, CustomPagination):
    serializer_class = SlideImageSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                instance = SlideImage.objects.get(id=id)
                data = self.serializer_class(instance, context={"request": request}).data
                response = {
                    "success": True,
                    "message": "Slide Image Get Successfully",
                    "data": data,
                }
                return Response(response, status=200)

            instance = SlideImage.objects.filter(Q(display_until__gte=timezone.now().date()) | Q(display_until__isnull=True)).order_by('-upload_date')
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True, context={"request": request})
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]
                total = result.data["count"]
            else:
                serializer = self.serializer_class(instance, many=True, context={"request": request})
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Slide Image List Get Successfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            MAX_IMAGE_SIZE_MB = 2
            data = request.data
            image = request.FILES.get("image")
            display_until = data.get("display_until", None) or None

            # ===== VALIDATIONS =====
            if not image:
                return self._error("Image is required", status=400)

            # 1️⃣ File Type Check
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                return self._error("Only JPG and PNG images are allowed", status=400)

            # 2️⃣ File Size Check (in MB)
            if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                return self._error(f"Image must be smaller than {MAX_IMAGE_SIZE_MB}MB", status=400)

            # 3️⃣ Display Until Validation
            if display_until:
                try:
                    display_until = datetime.strptime(display_until, "%Y-%m-%d").date()
                except ValueError:
                    return self._error("Invalid date format for display_until (YYYY-MM-DD expected)", status=400)
                
                if display_until < date.today():
                    return self._error("Display until date cannot be in the past", status=400)
            else:
                display_until = None


            with transaction.atomic():
                instance = SlideImage.objects.create(
                    uploaded_by=request.user,
                    image=image,
                    display_until=display_until
                )

                return Response({
                    "success": True,
                    "message": "Automation Job Created Successfully",
                    "data": self.serializer_class(instance,  context={"request": request}).data,
                })

        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)
    def delete(self, request, id=None):
        """
        Partial update of an AutomationJob (only provided fields are updated)
        """
        try:
            if not id:
                return self._error("Slide Image ID is required for Delete", status=400)
            
            data = request.data
            instance = SlideImage.objects.get(id=id)
            
            # Validate the requesting user has permission to update
            if not (request.user.is_superuser or instance.uploaded_by == request.user):
                return self._error("You can only Delete the Slide Image that you uploaded", status=400)
            
            # Update the instance with provided fields only
            with transaction.atomic():
                
                if os.path.exists(instance.image.path):
                    os.remove(instance.image.path)
                
                instance.delete()
                
                return Response({
                    "success": True,
                    "message": "Slide Image Deleted successfully",
                    "data": {"id": id}
                })
                
        except SlideImage.DoesNotExist:
            return self._error("Slide Image not found", status=400)
        except Exception as e:
            ExceptionDetails(e)
            return self._error(str(e), status=400)

    def _error(self, message, status=400):
        return Response({"success": False, "message": message}, status=status)
  
    
class ScreenerDashboardAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        try:
            # --- 1. Define Financial Year Dates (April 1st to March 31st assumed) ---
            
            current_date = timezone.now()
            current_year = current_date.year
            
            start_date_last_fy = datetime(current_year - 1, 4, 1)
            end_date_last_fy = datetime(current_year, 3, 31, 23, 59, 59)

            start_date_this_fy = datetime(current_year, 4, 1)
            end_date_this_fy = current_date.replace(tzinfo=None)  # Make current_date naive
            
            # NOTE: You MUST replace 'Completed' with the actual value from LAB_STATUS_CHOICES
            COMPLETED_STATUS = 'Completed' 
            
            data = {}

            # --- 2. Function to get counts for a given date range ---
            def get_job_counts(start_dt, end_dt):
                counts = {}
                
                # 1. AutomationJob: Filter by job_completion_time
                counts['AutomationJob'] = AutomationJob.objects.filter(
                    job_completion_time__gte=start_dt,
                    job_completion_time__lte=end_dt
                ).count()
                
                # 2. PowerLabJob & 3. RepairLabJob: Filter by status='Completed' AND completion date
                lab_filter = Q(
                    Q(status=COMPLETED_STATUS,
                      work_order_completion_date__gte=start_dt.date(),
                      work_order_completion_date__lte=end_dt.date()) |
                    Q(status=COMPLETED_STATUS,
                      work_order_completion_date__isnull=True, # Fallback to updated_at
                      updated_at__gte=start_dt,
                      updated_at__lte=end_dt)
                )

                counts['PowerLabJob'] = PowerLabJob.objects.filter(lab_filter).count()
                counts['RepairLabJob'] = RepairLabJob.objects.filter(lab_filter).count()

                # 4, 5, 6. Other Jobs: Filter by updated_at (as a proxy for completion)
                
                counts['WeighingMaintenanceJob'] = WeighingMaintenanceJob.objects.filter(
                    updated_at__gte=start_dt, updated_at__lte=end_dt
                ).count()

                counts['WeighingOperationJob'] = WeighingOperationJob.objects.filter(
                    updated_at__gte=start_dt, updated_at__lte=end_dt
                ).count()
                
                counts['CCTVJob'] = CCTVJob.objects.filter(
                    updated_at__gte=start_dt, updated_at__lte=end_dt
                ).count()

                return counts

            # --- 3. Execute Queries and Combine Data ---
            data_last_fy = get_job_counts(start_date_last_fy, end_date_last_fy)
            data_this_fy = get_job_counts(start_date_this_fy, end_date_this_fy)
            
            for job_name, last_fy_count in data_last_fy.items():
                data[job_name] = {
                    "last_fy_count": last_fy_count,
                    "this_fy_count": data_this_fy.get(job_name, 0)
                }

            # --- 4. Construct and Return Response ---
            resp_data = {
                "success": True,
                "message": "Screener Dashboard Data",
                "data": data,
            }
            return Response(resp_data)
            
        except Exception as e:
            # Assuming 'ExceptionDetails' is a custom logger
            # ExceptionDetails(e) 
            response = {
                "success": False,
                "message": f"Error retrieving dashboard data: {str(e)}",
            }
            return Response(response, status=400)

class ScreenerSlidesAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = ScreenerSlidesSerializer
    
    def get(self, request, id=None):
        try:
            instance = SlideImage.objects.filter(Q(display_until__gte=timezone.now().date()) | Q(display_until__isnull=True)).order_by('-upload_date')
            serializer = self.serializer_class(instance, many=True, context={"request": request})
            data = serializer.data
            response = {
                "success": True,
                "message": "Screener Slide Image List Get Successfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            ExceptionDetails(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)