import os
from django.http import FileResponse
from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from AuthApp.pagination import CustomPagination
from core.utility import Syserror, get_file_name
from .serializers import (
    SirSerializer,
    StabilityCertificationSerializer,
    ComplianceSerializer,
    SIRLogSerializer,
    SIRLogExcelSerializer,
    StabilityCertificationLogSerializer,
    StabilityCertificationLogExcelSerializer,
    ComplianceLogSerializer,
    ComplianceLogExcelSerializer,
    )
from .models import *
from django.db.models import Q, Value, F
from django.db.models.functions import Concat
from django.db import transaction
from rest_framework.response import Response
from AuthApp.customAuth import allowed_admin_user, allowed_superadmin
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile


# SIR

class SirApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = SirSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                    instance = SIR.objects.get(filter_criteria)
                except SIR.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "SIR doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "SIR retrieved successfully.",
                    "result": serializer.data
                }
                return Response(response, status=200)
            
            else:
                filter_criteria = Q(is_archive=False)
                if request.user.role == "User":
                        filter_criteria &= Q(is_approved=True)
                        
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                    Q(sir_number__icontains=query)
                        | Q(department__department_id__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(unit__unit_id__icontains=query)
                        | Q(unit__name__icontains=query)
                        | Q(title__icontains=query)
                        | Q(description__icontains=query)
                    )

                instance = SIR.objects.filter(filter_criteria).order_by("-created_at").distinct()
                # Paginate the results using the custom pagination class
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)

                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result

                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "SIR retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            sir_number = data.get("sir_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            year_of_inspection = data.get("year_of_inspection", None) or None
            description = data.get("description", None) or None
            compliance = data.get("compliance", "YES")
            attachment = data.get("file", None) or None
                        
            if not all([sir_number,department,year_of_inspection,attachment]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if SIR.objects.filter(sir_number=sir_number).exists():
                response = {
                    "success": False,
                    "message": "SIR number already exist.",
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required attachment."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance = SIR.objects.create(
                    sir_number = sir_number,
                    department = department,
                    unit = unit,
                    year_of_inspection = year_of_inspection,
                    compliance=compliance,
                    description = description,
                    attachment = attachment,
                    is_approved = request.user.is_superuser
                )
                instance.save()
                # log
                SIRLog.objects.create(
                    user = request.user,
                    sir = instance,
                    status = "Add SIR",
                    message = "SIR Added",
                    details = f"SIR data added"
                )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "SIR created successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
          
    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            id = data.get("id", None) or None
            sir_number = data.get("sir_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            year_of_inspection = data.get("year_of_inspection", None) or None
            compliance = data.get("compliance", "YES") 
            description = data.get("description", None) or None
            attachment = data.get("file", None) or None
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = SIR.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "SIR not found."
                }
                return Response(response, status=400)

            if SIR.objects.filter(sir_number=sir_number).exclude(sir_number=instance.sir_number).exists():
                response = {
                    "success": False,
                    "message": "SIR number already exist.",
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            
            
            log_details = ""
            with transaction.atomic():
                if instance.sir_number != sir_number:
                    log_details += f"SIR Number : {instance.sir_number} ➡️ {sir_number} |"
                    instance.sir_number = sir_number
                    
                if instance.department != department:
                    log_details += f"Department : {instance.department.name if department else None} ➡️ {department.name if department else None} |"
                    instance.department = department
                    
                if instance.unit != unit:
                    log_details += f"Unit : {instance.unit.name if unit else None} ➡️ {unit.name if unit else None} |"
                    instance.unit = unit
                    
                if instance.year_of_inspection != year_of_inspection:
                    log_details += f"Year of Inspection : {instance.year_of_inspection} ➡️ {year_of_inspection} |"
                    instance.title = year_of_inspection
                    
                if instance.description != description:
                    log_details += f"Description : {instance.description} ➡️ {description} |"
                    instance.description = description

                if instance.compliance != compliance:
                    log_details += f"Compliance : {instance.compliance} ➡️ {compliance} |"
                    instance.compliance = compliance
                
                if attachment:
                    if instance.attachment != attachment:
                        log_details += f"Attachment : {instance.attachment} ➡️ {attachment} |"
                        instance.attachment = attachment
                
                instance.save()
                
                # create log for update
                if log_details:
                    SIRLog.objects.create(          
                        user = request.user,
                        sir = instance,
                        status = "Update SIR",
                        message = "SIR updated",
                        details = log_details
                    )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "SIR updated successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

class ArchiveSIRApiView(APIView):
    serializer_class = SirSerializer
    
    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=True)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(sir_number__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__name__icontains=query)
                    | Q(title__icontains=query)
                    | Q(description__icontains=query)
                )
            instance = SIR.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "SIR retrieved successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    #archive single SIR
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if not id:
                response = {"success": False, "message": "Required SIR ID"}
                return Response(response, status=400)
        
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)

            try:
                sir = SIR.objects.get(id=id)
            except SIR.DoesNotExist:
                response = {
                    "success": False,
                    "message": "SIR doesn't exist."
                }
                return Response(response, status=400)

            if is_archive:
                SIRLog.objects.create(
                    user = request.user,
                    sir = sir,
                    status = "Archive SIR",
                    message = "SIR archived",
                    details = f"Archive reason : {archive_reason}."
                )
            else:
                archive_reason = None
                SIRLog.objects.create(
                    user = request.user,
                    sir = sir,
                    status = "Update SIR",
                    message = "SIR unarchived",
                    details = f"Archive reason : {sir.archive_reason} ➡️ None."
                )
            sir.is_archive = is_archive
            sir.archive_reason = archive_reason
            sir.save()
            response = {
                "success": True,
                "message": f'SIR {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
         
    # unarchive list of SIR
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            sir_id_list = data.get("sir_id_list", [])
            if not sir_id_list:
                response = {"success": False, "message": "Required SIR list"}
                return Response(response, status=400)
        
            for sir in SIR.objects.filter(id__in=sir_id_list, is_archive=True):
                SIRLog.objects.create(
                    user = request.user,
                    sir = sir,
                    status = "Update SIR",
                    message = "SIR unarchived",
                    details = f"Archive reason : {sir.archive_reason} ➡️ None."
                )
                sir.is_archive=False
                sir.archive_reason=None
                sir.save()
            response = {
                "success": True,
                "message": "SIR removed from archive successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
                 
class ApproveSIRApiView(APIView):
    
    def get(self, request):
        instance = SIR.objects.select_related().filter(is_archive=False, is_approved=False).order_by("-created_at").distinct()
        serializer = SirSerializer(instance, many=True)
        response = {
            "success": True,
            "message": "Pending SIR",
            "results": serializer.data
        }
        return Response(response, status=200)
    
    # approve single standard
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            if not id:
                response = {
                    "success": False,
                    "message": "Required SIR ID."
                }
                return Response(response, status=400)
            try:
                sir = SIR.objects.get(id=id, is_approved=False)
            except SIR.DoesNotExist:
                response = {
                    "success": False,
                    "message": "SIR doesn't exist."
                }
                return Response(response, status=400)
            sir.is_approved = True
            sir.save()
            response = {
                "success": True,
                "message": "SIR approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
    # approve mutliple standard
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            sir_id_list = data.get("sir_id_list", [])
            if not sir_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one SIR ID."
                }
                return Response(response, status=400)
            SIR.objects.filter(id__in=sir_id_list, is_archive=False, is_approved=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "SIR approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

class SIRLogApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = SIRLogSerializer
    
    @allowed_admin_user
    def get(self, request, sir_id=None):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            sir_list = request.GET.get("sir", None)
            if sir_id:
                try:
                    if request.user.role == "User":
                        sir = SIR.objects.get(id=sir_id, is_archive=False, is_approved=True)
                    else:
                        sir = SIR.objects.get(id=sir_id)
                    filter_criteria &= Q(sir=sir)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                            | Q(status__icontains=query)
                        )  
                except SIR.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "SIR doesn't exist."
                    }
                    return Response(response, status=400)
            else:
                if query:
                    filter_criteria &= Q(
                        Q(sir__sir_number__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
        
            if sir_list:
                filter_criteria &= Q(sir__id__in=sir_list.split(','))

            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                SIRLog.objects.select_related("user").filter(filter_criteria).order_by("-action_time").distinct()
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "results": serializer.data,
                "count": instance.count()
            }
            return Response(response, status=200)
     
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

class DownloadSIRFileApiView(APIView):
    def get(self, request, id):
        try:
            try:
                instance = SIR.objects.get(id=id)
            except SIR.DoesNotExist:
                response = {
                    "success": False,
                    "message": "SIR doesn't exist."
                }
                return Response(response, status=400)
            if instance.attachment:
                file_path = instance.attachment.path
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, "rb"))
                    SIRLog.objects.create(
                        user = request.user,
                        sir = instance,
                        status = "View SIR",
                        message = "View SIR File",
                        details = f'SIR file {get_file_name(file_path)} viewed.'
                    )
                    return response
                else:
                    return Response({"success": False, "message": "File not found."}, status=400)
            else:
                response = {
                    "success": False,
                    "message": "SIR file doesn't exist."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
class DownloadSIRLogExcelApiView(APIView):
    serializer_class = SIRLogExcelSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            sir_list = request.GET.get("sir", None)
            if query:
                filter_criteria &= Q(
                    Q(sir__sir_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
                
            if sir_list:
                filter_criteria &= Q(sir__id__in=sir_list.split(','))
                
            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                SIRLog.objects.select_related().filter(filter_criteria).order_by("-action_time").distinct()
            )
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "count": instance.count(),
                "results": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
            
class BulkArchiveSIRApiView(APIView):
    serializer_class = SirSerializer

    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=False)
            if department := request.GET.get("department_id"):
                filter_criteria &= Q(department__department_id=department)
            if unit := request.GET.get("unit_id"):
                filter_criteria &= Q(unit__unit_id=unit)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(sir_number__icontains=query)
                    | Q(department__department_id__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__unit_id__icontains=query)
                    | Q(unit__name__icontains=query)
                    | Q(title__icontains=query)
                    | Q(description__icontains=query)
                )
            instance = SIR.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve bulk archive SIR successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            sir_id_list = data.get("sir_id_list", [])
            archive_reason = data.get("archive_reason", None)
            
            if not sir_id_list:
                response = {
                    "success": False,
                    "message": "Required SIR list."
                }
                return Response(response, status=400)
            
            if not archive_reason:
                response = {
                    "success": False,
                    "message": "Required archive reason."
                }
                return Response(response, status=400)
            
            for sir in SIR.objects.filter(id__in=sir_id_list, is_archive=False):
                sir.is_archive=True
                sir.archive_reason=archive_reason
                sir.save()
                SIRLog.objects.create(
                    user = request.user,
                    sir =sir,
                    status = "Archive SIR",
                    message = "SIR archived from bulk archive",
                    details = f"Archive reason : {archive_reason}."
                )
            response = {
                "success": True,
                "message": "SIR archived successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
    
class SIRPermanentDeleteApiView(APIView):
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            sir_id_list = data.get("sir_id_list", [])
            if not sir_id_list:
                response = {"success": False, "message": "Required SIR list"}
                return Response(response, status=400)
            
            sir = SIR.objects.filter(id__in=sir_id_list, is_archive=True)
            if not sir:
                response = {
                    "success": False,
                    "message": "No SIR found."
                }
                return Response(response, status=400)
            for i in sir:
                i.sirlog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.sir_number} DELETED)"),)
                    ).update(message=F("new_message"))
                SIRLog.objects.create(
                    user = request.user,
                    sir = None,
                    status = "Delete SIR",
                    message = f"SIR {i.sir_number} deleted.",
                    details = f"SIR {i.sir_number} DELETED."
                )
                # attachment deletion will handle by model signal
                i.delete()
            response = {
                "success": True,
                "message": "SIR deleted successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
 


# STABILITY CERTIFICATION
       
class StabilityCertificationApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = StabilityCertificationSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                    instance = StabilityCertification.objects.get(filter_criteria)
                except StabilityCertification.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Stability Certificate doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Stability Certificate retrieved successfully.",
                    "result": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q(is_archive=False)
                if request.user.role == "User":
                        filter_criteria &= Q(is_approved=True)
                        
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(certificate_number__icontains=query)
                        | Q(department__department_id__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(unit__unit_id__icontains=query)
                        | Q(unit__name__icontains=query)
                    )

                instance = StabilityCertification.objects.filter(filter_criteria).order_by("-created_at").distinct()

                # Paginate the results using the custom pagination class
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)

                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Stability Certificate retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
        
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
        
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            certificate_number = data.get("certificate_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            attachment = data.get("file", None) or None
        
            if not all([certificate_number, department, attachment]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if StabilityCertification.objects.filter(certificate_number=certificate_number).exists():
                response = {
                    "success": False,
                    "message": "Certificate Number already exist."
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required attachment."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance = StabilityCertification.objects.create(
                    certificate_number = certificate_number,
                    department = department,
                    unit = unit,
                    attachment = attachment,
                    is_approved = request.user.is_superuser
                )
                instance.save()
                # log
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification = instance,
                    status = "Add Stability Certificate",
                    message = "Stability Certificate Added",
                    details = f"Stability Certificate data added"
                )
                
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Stability Certificate created successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)

        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
    
       
    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            id = data.get("id", None) or None
            certificate_number = data.get("certificate_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            attachment = data.get("file", None) or None
        
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = StabilityCertification.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Stability Certificate not found."
                }
                return Response(response, status=400)
            
            if StabilityCertification.objects.filter(certificate_number=certificate_number).exclude(certificate_number=instance.certificate_number).exists():
                response = {
                    "success": False,
                    "message": "Certificate Number already exist."
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
        
            
            log_details = ""
            with transaction.atomic():
                if instance.certificate_number != certificate_number:
                    log_details += f"Certificate Number : {instance.certificate_number} ➡️ {certificate_number} |"
                    instance.certificate_number = certificate_number
                
                if instance.department != department:
                    log_details += f"Department : {instance.department.name if department else None} ➡️ {department.name if department else None} |"
                    instance.department = department
                    
                if instance.unit != unit:
                    log_details += f"Unit : {instance.unit.name if unit else None} ➡️ {unit.name if unit else None} |"
                    instance.unit = unit
                
                if attachment:
                    if instance.attachment != attachment:
                        log_details += f"Attachment : {instance.attachment} ➡️ {attachment} |"
                        instance.attachment = attachment
                
                instance.save()
                # create log for update
                if log_details:
                    StabilityCertificationLog.objects.create(          
                        user = request.user,
                        stability_certification = instance,
                        status = "Update Stability Certificate",
                        message = "Stability Certificate updated",
                        details = log_details
                    )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Stability Certificate updated successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)

        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

class ArchiveStabilityCertificationApiView(APIView):
    serializer_class = StabilityCertificationSerializer
    
    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=True)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(certificate_number__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__name__icontains=query)
                )
            instance = StabilityCertification.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Stability Certificate retrieved successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    
    #archive single Stability Certification
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if not id:
                response = {"success": False, "message": "Required Stability Certificate ID"}
                return Response(response, status=400)
        
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)

            try:
                stability_certification = StabilityCertification.objects.get(id=id)
            except StabilityCertification.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Stability Certificate doesn't exist."
                }
                return Response(response, status=400)

            if is_archive:
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification = stability_certification,
                    status = "Archive Stability Certificate",
                    message = "Stability Certificate archived",
                    details = f"Archive reason : {archive_reason}."
                )
            else:
                archive_reason = None
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification = stability_certification,
                    status = "Update Stability Certificate",
                    message = "Stability Certificate unarchived",
                    details = f"Archive reason : {stability_certification.archive_reason} ➡️ None."
                )
            stability_certification.is_archive = is_archive
            stability_certification.archive_reason = archive_reason
            stability_certification.save()
            response = {
                "success": True,
                "message": f'Stability Certificate {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    # unarchive list of Stability certificate
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            stability_certification_id_list = data.get("stability_certificate_id_list", [])
            if not stability_certification_id_list:
                response = {"success": False, "message": "Required Stability Certificate list"}
                return Response(response, status=400)
        
            for stability_certification in StabilityCertification.objects.filter(id__in=stability_certification_id_list, is_archive=True):
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification = stability_certification,
                    status = "Update Stability Certificate",
                    message = "Stability Certificate unarchived",
                    details = f"Archive reason : {stability_certification.archive_reason} ➡️ None."
                )
                stability_certification.is_archive=False
                stability_certification.archive_reason=None
                stability_certification.save()
            response = {
                "success": True,
                "message": "Stability Certificate removed from archive successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

class ApproveStabilityCertificationApiView(APIView):
    def get(self, request):
        instance = StabilityCertification.objects.select_related().filter(is_archive=False, is_approved=False).order_by("created_at").distinct()
        serializer = StabilityCertificationSerializer(instance, many=True)
        response = {
            "success": True,
            "message": "Pending Stability Certificate",
            "results": serializer.data
        }
        return Response(response, status=200)
    
    # approve single Stability Certification
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            if not id:
                response = {
                    "success": False,
                    "message": "Required Stability Certificate ID."
                }
                return Response(response, status=400)
            try:
                instance = StabilityCertification.objects.get(id=id, is_approved=False)
            except StabilityCertification.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Stability Certificate doesn't exist."
                }
                return Response(response, status=400)
            instance.is_approved = True
            instance.save()
            response = {
                "success": True,
                "message": "Stability Certificate approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
    
    # approve mutliple Stability Certification
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            stability_certification_id_list = data.get("sc_id_list", [])
            if not stability_certification_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one Stability Certificate ID."
                }
                return Response(response, status=400)
            StabilityCertification.objects.filter(id__in=stability_certification_id_list, is_archive=False, is_approved=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "Stability Certificate approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

class StabilityCertificationLogApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = StabilityCertificationLogSerializer
    
    @allowed_admin_user
    def get(self, request, sc_id=None):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            if sc_id:
                try:
                    if request.user.role == "User":
                        stability_certification = StabilityCertification.objects.get(id=sc_id, is_archive=False, is_approved=True)
                    else:
                        stability_certification = StabilityCertification.objects.get(id=sc_id)
                    filter_criteria &= Q(stability_certification=stability_certification)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                            | Q(status__icontains=query)
                        )  
                except StabilityCertification.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Stability Certificate doesn't exist."
                    }
                    return Response(response, status=400)
            else:
                if query:
                    filter_criteria &= Q(
                        Q(stability_certification__certificate_number__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
        
            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                StabilityCertificationLog.objects.select_related("user").filter(filter_criteria).order_by("-action_time").distinct()
            )
            
            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            response = {
                "results": serializer.data,
                "count": instance.count()
            }
            return Response(response, status=200)
     
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
            
class DownloadStabilityCertificationFileApiView(APIView):
    def get(self, request, id):
        try:
            try:
                instance = StabilityCertification.objects.get(id=id)
            except StabilityCertification.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Stability Certificate doesn't exist."
                }
                return Response(response, status=400)
            if instance.attachment:
                file_path = instance.attachment.path
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, "rb"))
                    StabilityCertificationLog.objects.create(
                        user = request.user,
                        stability_certification = instance,
                        status = "View Stability Certificate",
                        message = "View Stability Certificate File",
                        details = f'Stability Certificate file {get_file_name(file_path)} viewed.'
                    )
                    return response
                else:
                    return Response({"success": False, "message": "File not found."}, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Stability Certificate file doesn't exist."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
                        
class DownloadStabilityCertificationLogExcelApiView(APIView):
    serializer_class = StabilityCertificationLogExcelSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            stability_certification_list = request.GET.get("stability_certification_list", None)
            if query:
                filter_criteria &= Q(
                    Q(stability_certification__certificate_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
                
            if stability_certification_list:
                filter_criteria &= Q(stability_certification__id__in=stability_certification_list.split(','))
            
            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                StabilityCertificationLog.objects.select_related().filter(filter_criteria).order_by("-action_time").distinct()
            )
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "count": instance.count(),
                "results": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

class BulkArchiveStabilityCertificationApiView(APIView):
    serializer_class = StabilityCertificationSerializer

    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=False)
            if department := request.GET.get("department_id"):
                filter_criteria &= Q(department__department_id=department)
            if unit := request.GET.get("unit_id"):
                filter_criteria &= Q(unit__unit_id=unit)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(certificate_number__icontains=query)
                    | Q(department__department_id__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__unit_id__icontains=query)
                    | Q(unit__name__icontains=query)
                )
            instance = StabilityCertification.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve bulk archive Stability Certificate successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            stability_certification_id_list = data.get("stability_certificate_id_list", [])
            archive_reason = data.get("archive_reason", None)
            
            if not stability_certification_id_list:
                response = {
                    "success": False,
                    "message": "Required Stability Certificate list."
                }
                return Response(response, status=400)
            
            if not archive_reason:
                response = {
                    "success": False,
                    "message": "Required archive reason."
                }
                return Response(response, status=400)
            
            for stability_certification in StabilityCertification.objects.filter(id__in=stability_certification_id_list, is_archive=False):
                stability_certification.is_archive=True
                stability_certification.archive_reason=archive_reason
                stability_certification.save()
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification =stability_certification,
                    status = "Archive Stability Certificate",
                    message = "Stability Certificate archived from bulk archive",
                    details = f"Archive reason : {archive_reason}."
                )
            response = {
                "success": True,
                "message": "Stability Certificate archived successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
               
class StabilityCertificationPermanentDeleteApiView(APIView):
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            stability_certification_id_list = data.get("stability_certificate_id_list", [])
            if not stability_certification_id_list:
                response = {"success": False, "message": "Required Stability Certificate list"}
                return Response(response, status=400)     
            
            stability_certification = StabilityCertification.objects.filter(id__in=stability_certification_id_list, is_archive=True)
            if not stability_certification:
                response = {
                    "success": False,
                    "message": "No Stability Certificate found."
                }
                return Response(response, status=400)
            for i in stability_certification:
                i.stabilitycertificationlog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.certificate_number} DELETED)"),)
                    ).update(message=F("new_message"))
                StabilityCertificationLog.objects.create(
                    user = request.user,
                    stability_certification = None,
                    status = "Delete Stability Certificate",
                    message = f"Stability Certificate {i.certificate_number} deleted.",
                    details = f"Stability Certificate {i.certificate_number} DELETED."
                )
                # attachment deletion will handle by model signal
                i.delete()      
            response = {
                "success": True,
                "message": "Stability Certificate deleted successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
                
            
            
# COMPLIANCE

class ComplianceApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = ComplianceSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                        
                    instance = Compliance.objects.get(filter_criteria)
                except Compliance.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Compliance doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Compliance retrieved successfully.",
                    "result": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q(is_archive=False)
                if request.user.role == "User":
                        filter_criteria &= Q(is_approved=True)
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(reference_number__icontains=query)
                        | Q(department__department_id__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(unit__unit_id__icontains=query)
                        | Q(unit__name__icontains=query)
                    )
                instance = Compliance.objects.filter(filter_criteria).order_by("-created_at").distinct()

                # Paginate the results using the custom pagination class
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)

                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result

                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Compliance retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)        
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
    
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            reference_number = data.get("reference_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            attachment = data.get("file", None) or None
 
            if not all([reference_number, department, attachment]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if Compliance.objects.filter(reference_number=reference_number).exists():
                response = {
                    "success": False,
                    "message": "Reference Number already exist."
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required attachment."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance = Compliance.objects.create(
                   reference_number = reference_number,
                   department = department,
                   unit = unit,
                   attachment = attachment,
                   is_approved = request.user.is_superuser
                )
                instance.save()
                # log
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = instance,
                    status = "Add Compliance",
                    message = "Compliance Added",
                    details = f"Compliance data added"
                )
                serializer = self.serializer_class(instance)
                response = {
                   "success": True,
                   "message": "Compliance created successfully.",
                   "results": serializer.data
                }
                return Response(response, status=200)

        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
    
    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            id = data.get("id", None) or None
            reference_number = data.get("reference_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            attachment = data.get("file", None) or None
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = Compliance.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Compliance not found."
                }
                return Response(response, status=400)
            
            if Compliance.objects.filter(reference_number=reference_number).exclude(reference_number=instance.reference_number).exists():
                response = {
                    "success": False,
                    "message": "Reference Number already exist."
                }
                return Response(response, status=400)
            
            if department:
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Department not found."
                    }
                    return Response(response, status=400)
            else:
                response = {
                        "success": False,
                        "message": "Required Department."
                    }
                return Response(response, status=400)
                
            if unit:
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Unit not found."
                    }
                    return Response(response, status=400)
            else:
                unit = None
                
            if attachment:
                is_attachment_valid = isinstance(attachment, InMemoryUploadedFile) or isinstance(attachment, UploadedFile)
                if not is_attachment_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = attachment.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file."
                    }
                    return Response(response, status=400)
            
            
            log_details = ""
            with transaction.atomic():
                if instance.reference_number != reference_number:
                    log_details += f"Reference Number : {instance.reference_number} ➡️ {reference_number} |"
                    instance.reference_number = reference_number
                    
                if instance.department != department:
                    log_details += f"Department : {instance.department.name if department else None} ➡️ {department.name if department else None} |"
                    instance.department = department
                    
                if instance.unit != unit:
                    log_details += f"Unit : {instance.unit.name if unit else None} ➡️ {unit.name if unit else None} |"
                    instance.unit = unit
                
                if attachment:
                    if instance.attachment != attachment:
                        log_details += f"Attachment : {instance.attachment} ➡️ {attachment} |"
                        instance.attachment = attachment
                
                instance.save()
                # create log for update
                if log_details:
                    ComplianceLog.objects.create(          
                        user = request.user,
                        compliance = instance,
                        status = "Update Compliance",
                        message = "Compliance updated",
                        details = log_details
                    )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Compliance updated successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)

        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
        
class ArchiveComplianceApiView(APIView):
    serializer_class = ComplianceSerializer
    
    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=True)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(reference_number__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__name__icontains=query)
                )
            instance = Compliance.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Compliance retrieved successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    #archive single Compliance
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if not id:
                response = {"success": False, "message": "Required Compliance ID"}
                return Response(response, status=400)
        
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)

            try:
                compliance = Compliance.objects.get(id=id)
            except Compliance.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Compliance doesn't exist."
                }
                return Response(response, status=400)

            if is_archive:
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = compliance,
                    status = "Archive Compliance",
                    message = "Compliance archived",
                    details = f"Archive reason : {archive_reason}."
                )
            else:
                archive_reason = None
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = compliance,
                    status = "Update Compliance",
                    message = "Compliance unarchived",
                    details = f"Archive reason : {compliance.archive_reason} ➡️ None."
                )
            compliance.is_archive = is_archive
            compliance.archive_reason = archive_reason
            compliance.save()
            response = {
                "success": True,
                "message": f'Compliance {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        
    # unarchive list of Compliance
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            compliance_id_list = data.get("compliance_id_list", [])
            if not compliance_id_list:
                response = {"success": False, "message": "Required Compliance list"}
                return Response(response, status=400)
        
            for compliance in Compliance.objects.filter(id__in=compliance_id_list, is_archive=True):
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = compliance,
                    status = "Update Compliance",
                    message = "Compliance unarchived",
                    details = f"Archive reason : {compliance.archive_reason} ➡️ None."
                )
                compliance.is_archive=False
                compliance.archive_reason=None
                compliance.save()
            response = {
                "success": True,
                "message": "Compliance removed from archive successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        
class ApproveComplianceApiView(APIView):
    
    def get(self, request):
        instance = Compliance.objects.select_related().filter(is_archive=False, is_approved=False).order_by("created_at").distinct()
        serializer = ComplianceSerializer(instance, many=True)
        response = {
            "success": True,
            "message": "Pending Compliance",
            "results": serializer.data
        }
        return Response(response, status=200)
    
    # approve single Compliance
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            id = data.get("id", None)
            if not id:
                response = {
                    "success": False,
                    "message": "Required Compliance ID."
                }
                return Response(response, status=400)
            try:
                compliance = Compliance.objects.get(id=id, is_approved=False)
            except Compliance.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Compliance doesn't exist."
                }
                return Response(response, status=400)
            compliance.is_approved = True
            compliance.save()
            response = {
                "success": True,
                "message": "Compliance approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    # approve mutliple Compliance
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            compliance_id_list = data.get("compliance_id_list", [])
            if not compliance_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one Compliance ID."
                }
                return Response(response, status=400)
            Compliance.objects.filter(id__in=compliance_id_list, is_archive=False, is_approved=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "Compliance approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
class ComplianceLogApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = ComplianceLogSerializer
    
    @allowed_admin_user
    def get(self, request, com_id=None):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            compliance_list = request.GET.get("compliance", None)
            if com_id:
                try:
                    if request.user.role == "User":
                        compliance = Compliance.objects.get(id=com_id, is_archive=False, is_approved=True)
                    else:
                        compliance = Compliance.objects.get(id=com_id)
                    filter_criteria &= Q(compliance=compliance)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                        )
                except Compliance.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Compliance doesn't exist."
                    }
                    return Response(response, status=400)
            else:
                if query:
                    filter_criteria &= Q(
                        Q(compliance__reference_number__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
        
            if compliance_list:
                filter_criteria &= Q(compliance__id__in=compliance_list.split(','))

            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                ComplianceLog.objects.select_related("user").filter(filter_criteria).order_by("-action_time").distinct()
            )
            
            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result
            serializer = self.serializer_class(instance, many=True)
            response = {
                "results": serializer.data,
                "count": instance.count()
            }
            return Response(response, status=200)
     
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
class DownloadComplianceFileApiView(APIView):
    def get(self, request, id):
        try:
            try:
                instance = Compliance.objects.get(id=id)
            except Compliance.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Compliance doesn't exist."
                }
                return Response(response, status=400)
            if instance.attachment:
                file_path = instance.attachment.path
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, "rb"))
                    ComplianceLog.objects.create(
                        user = request.user,
                        compliance = instance,
                        status = "View Compliance",
                        message = "View Compliance File",
                        details = f'Compliance file {get_file_name(file_path)} viewed.'
                    )
                    return response
                else:
                    return Response({"success": False, "message": "File not found."}, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Compliance file doesn't exist."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
class DownloadComplianceLogExcelApiView(APIView):
    serializer_class = ComplianceLogExcelSerializer

    def get(self, request):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            compliance_list = request.GET.get("compliance", None)
            if query:
                filter_criteria &= Q(
                    Q(compliance__reference_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )
            
            if status:
                filter_criteria &= Q(status__in=status.split(','))
                
            if compliance_list:
                filter_criteria &= Q(compliance__id__in=compliance_list.split(','))
                
            if from_date := request.GET.get("start_date", None):
                try:
                    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__gte=from_date)
                except ValueError:
                    pass
            if to_date := request.GET.get("end_date", None):
                try:
                    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                    filter_criteria &= Q(action_time__date__lte=to_date)
                except ValueError:
                    pass
            
            if user_id :
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                ComplianceLog.objects.select_related().filter(filter_criteria).order_by("-action_time").distinct()
            )
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "count": instance.count(),
                "results": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
class BulkArchiveComplianceApiView(APIView):
    serializer_class = ComplianceSerializer

    @allowed_admin_user
    def get(self, request):
        try:
            filter_criteria = Q(is_archive=False)
            if department := request.GET.get("department_id"):
                filter_criteria &= Q(department__department_id=department)
            if unit := request.GET.get("unit_id"):
                filter_criteria &= Q(unit__unit_id=unit)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(reference_number__icontains=query)
                    | Q(department__department_id__icontains=query)
                    | Q(department__name__icontains=query)
                    | Q(unit__unit_id__icontains=query)
                    | Q(unit__name__icontains=query)
                )
            instance = Compliance.objects.select_related('department').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve bulk archive Compliance successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
    
    
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            compliance_id_list = data.get("compliance_id_list", [])
            archive_reason = data.get("archive_reason", None)
            
            if not compliance_id_list:
                response = {
                    "success": False,
                    "message": "Required Compliance list."
                }
                return Response(response, status=400)
            
            if not archive_reason:
                response = {
                    "success": False,
                    "message": "Required archive reason."
                }
                return Response(response, status=400)
            
            for compliance in Compliance.objects.filter(id__in=compliance_id_list, is_archive=False):
                compliance.is_archive=True
                compliance.archive_reason=archive_reason
                compliance.save()
                
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = compliance,
                    status = "Archive Compliance",
                    message = "Compliance archived from bulk archive",
                    details = f"Archive reason : {archive_reason}."
                )
            response = {
                "success": True,
                "message": "Compliance archived successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        
class CompliancePermanentDeleteApiView(APIView):
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            compliance_id_list = data.get("compliance_id_list", [])
            if not compliance_id_list:
                response = {"success": False, "message": "Required Compliance list"}
                return Response(response, status=400)
            
            compliance = Compliance.objects.filter(id__in=compliance_id_list, is_archive=True)
            if not compliance:
                response = {
                    "success": False,
                    "message": "No Compliance found."
                }
                return Response(response, status=400)
            for i in compliance:
                i.compliancelog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.reference_number} DELETED)"),)
                    ).update(message=F("new_message"))
                ComplianceLog.objects.create(
                    user = request.user,
                    compliance = None,
                    status = "Delete Compliance",
                    message = f"Compliance {i.reference_number} deleted.",
                    details = f"Compliance {i.reference_number} DELETED."
                )
                # attachment deletion will handle by model signal
                i.delete()
            response = {
                "success": True,
                "message": "Compliance deleted successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        
        
