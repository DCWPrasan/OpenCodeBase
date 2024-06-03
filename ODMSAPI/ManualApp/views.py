import json
from django.shortcuts import render
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
# Create your views here.
from rest_framework.views import APIView
from django.db import transaction
from .serializers import (
    ManualSerializer,
    ManualDetailSerializer,
    ManualLogSerializer,
    ManualLogExcelSerializer,
    ManualArchiveSerializer
    )
from AuthApp.pagination import CustomPagination
from AuthApp.models import Department,Unit
from django.db.models import Q, Count, Value, F
from django.db.models.functions import Concat
from .models import Manual, ManualLog
from rest_framework.response import Response
from core.utility import Syserror, check_file, get_file_name
from django.http import FileResponse
from AuthApp.customAuth import allowed_superadmin, allowed_admin_user
from datetime import datetime
import os



class ManualAPIView(APIView):
    pagination_class = CustomPagination
    serializer_class = ManualSerializer
    
    def get(self, request, id=None):
        try:
            if request.user.role == "User" and not request.user.is_view_manual:
                response = {
                    "success": False,
                    "message": "Required permission to view."
                }
                return Response(response, status=400)
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                        
                    instance = Manual.objects.get(filter_criteria)
                    if instance.manual_type == "TECHNICAL CALCULATION":
                        if request.user.role == "User" and not request.user.is_view_technical_calculation:
                            response = {
                                "success": False,
                                "message": "Required permission to view."
                            }
                            return Response(response, status=400)
                except Manual.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Document doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = ManualDetailSerializer(instance)
                response = {
                    "success": True,
                    "message": "Document data retrieved successfully.",
                    "result" : serializer.data
                }
                return Response(response, status=200)
            else:
                manual_type = request.GET.get("manual_type", "MANUALS")
                if not manual_type:
                    manual_type = "MANUALS"
                filter_criteria = Q(manual_type=manual_type, is_archive=False)
                if request.user.role == "User":
                        filter_criteria &= Q(is_approved=True)
                        
                if query := request.GET.get("query"):
                    if manual_type == "MANUALS":
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(department__name__icontains=query)
                            | Q(unit__name__icontains=query)
                            | Q(supplier__icontains=query)
                            | Q(package_no__icontains=query)
                            | Q(letter_no__icontains=query)
                            | Q(registration_date__icontains=query)
                            | Q(description__icontains=query)
                            | Q(remarks__icontains=query)
                        )
                    elif manual_type == "REFERENCE BOOK":
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(editor__icontains=query)
                            | Q(source__icontains=query)
                            | Q(author__icontains=query)
                            | Q(description__icontains=query)
                        )
                    elif manual_type == "TENDER DOCUMENT":
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(department__name__icontains=query)
                            | Q(unit__name__icontains=query)
                            | Q(description__icontains=query)
                        )
                    elif manual_type == "CATALOUGE":
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(source__icontains=query)
                            | Q(description__icontains=query)
                        )
                    elif manual_type == "PROJECT REPORT":
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(description__icontains=query)
                            | Q(supplier__icontains=query)
                            | Q(capacity__icontains=query)
                            | Q(year__icontains=query)
                            | Q(remarks__icontains=query)
                        )
                    elif manual_type == "TECHNICAL CALCULATION":
                        if request.user.role == "User" and not request.user.is_view_manual:
                            response = {
                                "success": False,
                                "message": "Required permission to view."
                            }
                            return Response(response, status=400)
                    else:
                        filter_criteria &= Q(
                            Q(manual_type__icontains=query)
                            | Q(manual_no__icontains=query)
                            | Q(supplier__icontains=query)
                            | Q(department__name__icontains=query)
                            | Q(description__icontains=query)
                        )
                instance = Manual.objects.select_related("department").filter(filter_criteria).order_by("manual_no_numeric")
                
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
                    "message": "Document data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
    
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            manual_type = data.get("manual_type", None) or None
            manual_no = data.get("manual_number", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            supplier = data.get("supplier", None) or None
            package_no = data.get("package_number", None) or None
            letter_no = data.get("letter_number", None) or None
            registration_date = data.get("registration_date", None) or None
            description = data.get("description", None) or None
            remarks = data.get("remarks", None) or None
            editor = data.get("editor", None) or None
            source = data.get("source", None) or None
            author = data.get("author", None) or None
            capacity = data.get("capacity", None) or None
            year = data.get("year", None) or None
            file = data.get("file", None) or None
            
            if not all([manual_no, manual_type]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if manual_type in ["MANUALS", "TENDER DOCUMENT","TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
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
                    department = None
                    
            if manual_type in ["MANUALS", "TENDER DOCUMENT"]:
                if manual_type == "TENDER DOCUMENT":
                    package_no = None
                    letter_no = None
                    registration_date = None
                    remarks = None
                    supplier = None
                editor = None
                source = None
                author = None
                capacity = None
                year = None
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
                    
            elif manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
                department = None
                unit = None
                supplier = None
                package_no = None
                letter_no = None
                registration_date = None
                remarks = None
                capacity = None
                year = None
                if manual_type == "CATALOUGE":
                    editor = None
                    author = None
            elif manual_type in ["TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
                unit = None
                package_no = None
                letter_no = None
                registration_date = None
                remarks = None
                capacity = None
                year = None
                editor = None
                author = None
                source = None
                
            elif manual_type == "PROJECT REPORT":
                department = None
                unit = None
                package_no = None
                letter_no = None
                registration_date = None
                editor = None
                author = None
                source = None
            else:
                response = {
                    "success": False,
                    "message": "Invalid document type"
                }
                return Response(response, status=400)

            if file:
                is_file_valid = isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                if not is_file_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = file.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            else:
                file = None
            with transaction.atomic():
                instance = Manual.objects.create(
                    manual_no = manual_no,
                    manual_type = manual_type,
                    department = department,
                    unit = unit,
                    supplier = supplier,
                    package_no = package_no,
                    letter_no = letter_no,
                    registration_date = registration_date,
                    description = description,
                    remarks = remarks,
                    editor = editor,
                    source = source,
                    author = author,
                    capacity = capacity,
                    year = year,
                    upload_file = file,
                    is_approved = request.user.is_superuser
                )
                instance.save()
                # log
                ManualLog.objects.create(
                    user = request.user,
                    manual = instance,
                    status = "Add Document",
                    message = "Document added",
                    details = f'Document data added',
                )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Document created successfully.",
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
            department = data.get("department", None) or None
            unit = data.get("unit", None) or None
            supplier = data.get("supplier", None) or None
            package_no = data.get("package_number", None) or None
            letter_no = data.get("letter_number", None) or None
            registration_date = data.get("registration_date", None) or None
            description = data.get("description", None) or None
            remarks = data.get("remarks", None) or None
            editor = data.get("editor", None) or None
            source = data.get("source", None) or None
            author = data.get("author", None) or None
            capacity = data.get("capacity", None) or None
            year = data.get("year", None) or None
            file = data.get("file", None) or None            
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = Manual.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Document not found."
                }
                return Response(response, status=400)
            
            if instance.manual_type in ["MANUALS", "TENDER DOCUMENT","TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
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
                    department = None
                    
            if instance.manual_type in ["MANUALS", "TENDER DOCUMENT"]:
                if instance.manual_type == "TENDER DOCUMENT":
                    package_no = None
                    letter_no = None
                    registration_date = None
                    remarks = None
                    supplier = None
                editor = None
                source = None
                author = None
                capacity = None
                year = None
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
                    
            elif instance.manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
                department = None
                unit = None
                supplier = None
                package_no = None
                letter_no = None
                registration_date = None
                remarks = None
                capacity = None
                year = None
                if instance.manual_type == "CATALOUGE":
                    editor = None
                    author = None
            elif instance.manual_type in ["TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
                unit = None
                package_no = None
                letter_no = None
                registration_date = None
                remarks = None
                capacity = None
                year = None
                editor = None
                author = None
                source = None
                
            elif instance.manual_type == "PROJECT REPORT":
                department = None
                unit = None
                package_no = None
                letter_no = None
                registration_date = None
                editor = None
                author = None
                source = None
            else:
                response = {
                    "success": False,
                    "message": "Invalid document type"
                }
                return Response(response, status=400)
            
            if file:
                is_file_valid = isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                if not is_file_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = file.name.split(".")[-1].upper()
                if file_ext != "PDF":
                    response = {
                        "success": False,
                        "message": "Upload pdf file"
                    }
                    return Response(response, status=400)
            else:
                file = None
            log_details = ""
            with transaction.atomic():
                if instance.department != department:
                    log_details += f'Department : {instance.department.name if instance.department else None} ➡️ {department.name} |'
                    instance.department = department

                if instance.unit != unit:
                    log_details += f'Unit : {instance.unit.name if instance.unit else None} ➡️ {unit.name} |'
                    instance.unit = unit

                if instance.supplier != supplier:
                    log_details += f'Supplier : {instance.supplier} ➡️ {supplier} |'
                    instance.supplier = supplier

                if instance.package_no != package_no:
                    log_details += f'Package Number : {instance.package_no} ➡️ {package_no} |'
                    instance.package_no = package_no

                if instance.letter_no != letter_no:
                    log_details += f'Letter Number : {instance.letter_no} ➡️ {letter_no} |'
                    instance.letter_no = letter_no

                if instance.registration_date != registration_date:
                    log_details += f'Registration Date : {instance.registration_date} ➡️ {registration_date} |'
                    instance.registration_date = registration_date

                if instance.description != description:
                    log_details += f'Description : {instance.description} ➡️ {description} |'
                    instance.description = description

                if instance.remarks != remarks:
                    log_details += f'Remarks : {instance.remarks} ➡️ {remarks} |'
                    instance.remarks = remarks

                if instance.editor != editor:
                    log_details += f'Editor : {instance.editor} ➡️ {editor} |'
                    instance.editor = editor

                if instance.source != source:
                    log_details += f'Source : {instance.source} ➡️ {source} |'
                    instance.source = source

                if instance.author != author:
                    log_details += f'Author : {instance.author} ➡️ {author} |'
                    instance.author = author

                if instance.capacity != capacity:
                    log_details += f'Capacity : {instance.capacity} ➡️ {capacity} |'
                    instance.capacity = capacity

                if instance.year != year:
                    log_details += f'Year : {instance.year} ➡️ {year} |'
                    instance.year = year

                if file:
                    log_details += f"Upload file : {get_file_name(instance.upload_file.name)} ➡️ {file.name} |"
                    instance.upload_file = file
                    instance.is_approved = True if (not instance.is_approved and request.user.is_superuser) else False
                    
                instance.save()
                if log_details:
                    ManualLog.objects.create(   # create log for update
                        user=request.user,
                        manual=instance,
                        status="Update Document",
                        message="Document Updated",
                        details=log_details
                    )
                serializer = ManualDetailSerializer(instance)
                response = {
                    "success": True,
                    "message": "Document updated successfully.",
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

        
# view manual
class DownloadManualFileApiView(APIView):
    def get(self, request, id):
        try:
            if request.user.role == "User" and not request.user.is_view_manual:
                response = {
                    "success": False,
                    "message": "Required permission to view."
                }
                return Response(response, status=400)
            try:
                instance = Manual.objects.get(id=id)
            except Manual.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Document doesn't exist."
                }
                return Response(response, status=400)
            if instance.upload_file:
                file_path = instance.upload_file.path
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, "rb"))
                    ManualLog.objects.create(
                        user = request.user,
                        manual = instance,
                        status = "View Document",
                        message = "View Document File",
                        details = f'Document File {get_file_name(file_path)} viewed.'
                    )
                    return response
                else:
                    return Response({"success": False, "message": "File not found."}, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Document file doesn't exist."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
# approve
class ApproveManualApiView(APIView):
    @allowed_superadmin
    def get(self, request):
        manual_type = request.GET.get("manual_type", "MANUALS")
        instance = Manual.objects.select_related().filter(manual_type=manual_type, is_archive=False, is_approved=False).order_by("-created_at").distinct()
        serializer = ManualDetailSerializer(instance, many=True)
        response = {
            "success": True,
            "message": "Pending Document",
            "results": serializer.data,
        }
        return Response(response, status=200)
    
    # approve single manual
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            manual_id = data.get("id", None)
            if not manual_id:
                response = {
                    "success": False,
                    "message": "Required Document ID."
                }
                return Response(response, status=400)
            try:
                manual = Manual.objects.get(id=manual_id, is_approved=False)
            except Manual.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Document doesn't exist."
                }
                return Response(response, status=400)
            
            manual.is_approved = True
            manual.save()
            response = {
                "success": True,
                "message": "Document approved successfully."
            }
            return Response(response, status=200)
            
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
    # approve multiple manual
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            manual_id_list = data.get("manual_id_list", [])
            if not manual_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one Document ID."
                }
                return Response(response, status=400)

            Manual.objects.filter(id__in=manual_id_list, is_archive=False, is_approved=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "Document approved successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

# archive
class ArchiveManualApiView(APIView):
    serializer_class = ManualArchiveSerializer
    
    @allowed_superadmin
    def get(self, request):
        try:
            manual_type = request.GET.get("manual_type", "MANUALS")
            filter_criteria = Q(manual_type=manual_type, is_archive=True)
            if query := request.GET.get("query"):
                if manual_type == "MANUALS":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(department__icontains=query)
                        | Q(unit__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(package_no__icontains=query)
                        | Q(letter_no__icontains=query)
                        | Q(registration_date__icontains=query)
                        | Q(description__icontains=query)
                        | Q(remarks__icontains=query)
                    )
                elif manual_type == "REFERENCE BOOK":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(editor__icontains=query)
                        | Q(source__icontains=query)
                        | Q(author__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "TENDER DOCUMENT":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(department__icontains=query)
                        | Q(unit__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "CATALOUGE":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(source__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "PROJECT REPORT":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(description__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(capacity__icontains=query)
                        | Q(year__icontains=query)
                        | Q(remark__icontains=query)
                    )
                else:
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(department__icontains=query)
                        | Q(description__icontains=query)
                    )
            instance = Manual.objects.select_related("department").filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Document data retrieved successfully.",
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
    
    # archive single manual
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            manual_id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)
            if not manual_id:
                response = {"success": False, "message": "Required Document ID"}
                return Response(response, status=400)
            try:
                manual = Manual.objects.get(id=manual_id)
            except Manual.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Document doesn't exist."
                }
                return Response(response, status=400)
            if is_archive:
                ManualLog.objects.create(
                    user = request.user,
                    manual = manual,
                    status = "Archive Document",
                    message = "Document archived",
                    details = f"Document reason : {archive_reason}."
                )
            else:
                archive_reason = None
                ManualLog.objects.create(
                    user = request.user,
                    manual = manual,
                    status = "Update Document",
                    message = "Document unarchived",
                    details = f"Archive reason : {manual.archive_reason} ➡️ None."
                )
            manual.is_archive = is_archive
            manual.archive_reason = archive_reason
            manual.save()
            response = {
                "success": True,
                "message": f'Document {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
    
    # unarchive list of manual
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            manual_id_list = data.get("manual_id_list", [])
            if not manual_id_list:
                response = {
                    "success": False,
                    "message": "Required Document list."
                }
                return Response(response, status=400)
            
            for manual in Manual.objects.filter(id__in=manual_id_list, is_archive=True):
                ManualLog.objects.create(
                    user = request.user,
                    manual = manual,
                    status = "Update Document",
                    message = "Document unachived",
                    details = f"Archive reason : {manual.archive_reason} ➡️ None."
                )
                manual.is_archive=False
                manual.archive_reason=None
                manual.save()
            response = {
                "success": True,
                "message": "Document removed from archive successfully.",
            }
            return Response(response, status=200)
        
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

# delete
class ManualPermanentDeleteApiView(APIView):
    
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            manual_id_list = data.get("manual_id_list", [])
            if not manual_id_list:
                response = {"success": False, "message": "Required Document list"}
                return Response(response, status=400)
            
            manuals = Manual.objects.filter(id__in=manual_id_list, is_archive=True)
            if not manuals:
                response = {
                    "success": False,
                    "message": "No Document found."
                }
                return Response(response, status=400)
            for i in manuals:
                i.manuallog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.manual_type}-{i.manual_no} DELETED)"),)
                    ).update(message=F("new_message"))
                ManualLog.objects.create(
                    user = request.user,
                    manual = None,
                    status = "Delete Document",
                    message = f"{i.manual_type} deleted.",
                    details = f"Document {i.manual_type}-{i.manual_no} DELETED."
                )
                # attachment deletion will handle by model signal
                i.delete()
            response = {
                "success": True,
                "message": "Document deleted successfully."
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

# log
class ManualLogApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = ManualLogSerializer
    
    def get(self, request, manual_id=None):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            manual_list = request.GET.get("manual", None)
            manual_type = request.GET.get("manual_type", None)
            if manual_id:
                try:
                    if request.user.role == "User":
                        manual = Manual.objects.get(id=manual_id, is_archive=False, is_approved=True)
                        filter_criteria &= Q(user=request.user)
                    else:
                        manual = Manual.objects.get(id=manual_id)
                    filter_criteria &= Q(manual=manual)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                        )  
                except Manual.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Document doesn't exist."
                    }
                    return Response(response, status=400)
            else:
                if query:
                    filter_criteria &= Q(
                        Q(manual__manual_type__icontains=query)
                        | Q(manual__manual_no__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
            
            if manual_type:
                filter_criteria &= Q(manual__manual_type__in=manual_type.split(','))    
            
            if manual_list:
                filter_criteria &= Q(manual__id__in=manual_list.split(','))
                
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
                ManualLog.objects.select_related("user").filter(filter_criteria).order_by("-action_time").distinct()
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
        
# view log excel
class DownloadManualLogExcelApiView(APIView):
    serializer_class = ManualLogExcelSerializer
    
    def get(self, request):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            manual_list = request.GET.get("manual", None)
            if query:
                    filter_criteria &= Q(
                        Q(manual__manual_type__icontains=query)
                        | Q(manual__manual_no__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(','))
            if manual_list:
                filter_criteria &= Q(manual__id__in=manual_list.split(','))
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
                ManualLog.objects.select_related().filter(filter_criteria).order_by("-action_time").distinct()
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
        
# bulk archive
class BulkArchiveManualApiView(APIView):
    serializer_class = ManualSerializer
    
    @allowed_superadmin
    def get(self, request):
        try:
            manual_type = request.GET.get("manual_type", "MANUALS")
            filter_criteria = Q(manual_type=manual_type, is_archive=False)
            if query := request.GET.get("query"):
                if manual_type == "MANUALS":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(unit__name__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(package_no__icontains=query)
                        | Q(letter_no__icontains=query)
                        | Q(registration_date__icontains=query)
                        | Q(description__icontains=query)
                        | Q(remarks__icontains=query)
                    )
                elif manual_type == "REFERENCE BOOK":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(editor__icontains=query)
                        | Q(source__icontains=query)
                        | Q(author__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "TENDER DOCUMENT":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(unit__name__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "CATALOUGE":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(source__icontains=query)
                        | Q(description__icontains=query)
                    )
                elif manual_type == "PROJECT REPORT":
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(description__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(capacity__icontains=query)
                        | Q(year__icontains=query)
                        | Q(remarks__icontains=query)
                    )
                else:
                    filter_criteria &= Q(
                        Q(manual_type__icontains=query)
                        | Q(manual_no__icontains=query)
                        | Q(supplier__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(description__icontains=query)
                    )
            instance = Manual.objects.select_related("department").filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve bulk archive document successfully.",
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
            manual_id_list = data.get("manual_id_list", [])
            archive_reason = data.get("archive_reason", None)
            if not manual_id_list:
                response = {
                    "success": False,
                    "message": "Required document list."
                }
                return Response(response, status=400)
            
            if not archive_reason:
                response = {
                    "success": False,
                    "message": "Required archive reason."
                }
                return Response(response, status=400)
            
            for manual in Manual.objects.filter(id__in=manual_id_list, is_archive=False):
                manual.is_archive=True
                manual.archive_reason=archive_reason
                manual.save()
                ManualLog.objects.create(
                    user = request.user,
                    manual = manual,
                    status = "Archive Document",
                    message = "Document archived from bulk archive",
                    details = f"Archive reason : {archive_reason}."
                )
            response = {
                "success": True,
                "message": "Document archived successfully.",
            }
            return Response(response, status=200)
        
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        

class BulkUploadManualApiView(APIView):
    serializer_class = ManualSerializer
    
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            data_list = data.get("data_list", None)
            file_list = data.getlist("file_list", None)
            if not data_list:
                raise ValueError("Required data")
            try:
                data_list = json.loads(data_list)
            except:
                raise ValueError("Invalid format of data list.")
            
            new_data_list = []
            error_data_set = []
            for index, data in enumerate(data_list, start=2):
                manual_type = data.get("manual_type", "MANUALS")
                manual_no = data.get("manual_number", None) or None
                department = data.get("department_id", None) or None
                unit = data.get("unit_id", None) or None
                supplier = data.get("supplier", None) or None
                package_no = data.get("package_number", None) or None
                letter_no = data.get("letter_number", None) or None
                registration_date = data.get("registration_date", None) or None
                description = data.get("description", None) or None
                remarks = data.get("remarks", None) or None
                editor = data.get("editor", None) or None
                source = data.get("source", None) or None
                author = data.get("author", None) or None
                capacity = data.get("capacity", None) or None
                year = data.get("year", None) or None
                file = data.get("file", None) or None
                
                required_field = [
                    manual_no,
                    manual_type,
                ]
                
                if not all(required_field):
                    error_data_set.append(
                        {"row": index, "message": "Required mandatory fields."}
                    )
                    continue
                
                if manual_type in ["MANUALS", "TENDER DOCUMENT","TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
                    if department:
                        if department_exist := Department.objects.filter(department_id__icontains=department):
                            department = department_exist.first()
                        else:
                            error_data_set.append(
                                {"row": index, "message": "Department doesn't exist."}
                            )
                            continue
                    else:
                        department = None
                    
                if manual_type in ["MANUALS", "TENDER DOCUMENT"]:
                    if manual_type == "TENDER DOCUMENT":
                        package_no = None
                        letter_no = None
                        registration_date = None
                        remarks = None
                        supplier = None
                    editor = None
                    source = None
                    author = None
                    capacity = None
                    year = None
                    if unit:
                        if unit_exist := Unit.objects.filter(unit_id__icontains=unit):
                            unit = unit_exist.first()
                        else:
                            error_data_set.append(
                                {"row": index, "message": "Unit doesn't exist."}
                            )
                            continue
                    else:
                        unit = None
                        
                elif manual_type in ["REFERENCE BOOK", "CATALOUGE"]:
                    department = None
                    unit = None
                    supplier = None
                    package_no = None
                    letter_no = None
                    registration_date = None
                    remarks = None
                    capacity = None
                    year = None
                    if manual_type == "CATALOUGE":
                        editor = None
                        author = None
                elif manual_type in ["TECHNICAL CALCULATION", "TECHNICAL SPECIFICATION", "TECHNICAL REPORT"]:
                    unit = None
                    package_no = None
                    letter_no = None
                    registration_date = None
                    remarks = None
                    capacity = None
                    year = None
                    editor = None
                    author = None
                    source = None
                    
                elif manual_type == "PROJECT REPORT":
                    department = None
                    unit = None
                    package_no = None
                    letter_no = None
                    registration_date = None
                    editor = None
                    author = None
                    source = None
                else:
                    error_data_set.append(
                        {"row": index, "message": "Invalid manual type."}
                    )
                
                is_file_list_valid = all(
                    isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                    for file in file_list
                )
                if not is_file_list_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)

                if file:
                    if newfile := check_file(file_list, file):
                        file = newfile
                    else:
                        error_data_set.append(
                            {"row": index, "message": "File didn't match"}
                        )
                        continue
                if not error_data_set:
                    new_data_list.append({
                        "manual_no": manual_no,
                        "manual_type": manual_type,
                        "department": department,
                        "unit": unit,
                        "supplier": supplier,
                        "package_no": package_no,
                        "letter_no": letter_no,
                        "registration_date": registration_date,
                        "description": description,
                        "remarks": remarks,
                        "editor": editor,
                        "source": source,
                        "author": author,
                        "capacity": capacity,
                        "year": year,            
                        "file": file,
                    })
                    
            if not error_data_set:
                with transaction.atomic():
                    for data in new_data_list:
                        manual_type = data.get("manual_type")
                        manual_no = data.get("manual_no")
                        department = data.get("department")
                        unit = data.get("unit")
                        supplier = data.get("supplier")
                        package_no = data.get("package_no")
                        letter_no = data.get("letter_no")
                        registration_date = data.get("registration_date")
                        description = data.get("description")
                        remarks = data.get("remarks")
                        editor = data.get("editor")
                        author = data.get("author")
                        source = data.get("source")
                        capacity = data.get("capacity")
                        year = data.get("year")
                        file = data.get("file")
                        
                        instance = Manual.objects.create(
                            manual_type = manual_type,
                            manual_no = manual_no,
                            department = department,
                            unit = unit,
                            supplier = supplier,
                            package_no = package_no,
                            letter_no = letter_no,
                            registration_date = registration_date,
                            description = description,
                            remarks = remarks,
                            editor = editor,
                            author = author,
                            source = source,
                            capacity = capacity,
                            year = year,
                            upload_file = file,
                            is_approved = request.user.is_superuser
                        )
                        ManualLog.objects.create(
                            user = request.user,
                            manual = instance,
                            status = "Add Document",
                            message = "Document added from bulk upload.",
                            details = f"Add document data from bulk upload excel file."
                        )
                response = {
                    "success": True,
                    "message": "Document created successfully.",
                    "results": {
                        "error_data_set": error_data_set,
                    }
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Failed to create Document",
                    "results": {
                        "error_data_set": error_data_set,
                    }
                }
                return Response(response, status=400)
   
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
            
        
class ManualCountApiView(APIView):
    @allowed_admin_user
    def get(self, request):
        status_type = request.GET.get("status_type", "Approved")
        try:
            if status_type == "Approved":
                manual = Manual.objects.select_related().aggregate(
                    manuals_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="MANUALS")),
                    rb_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="REFERENCE BOOK")),
                    td_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="TENDER DOCUMENT")),
                    catalouge_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="CATALOUGE")),
                    tc_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="TECHNICAL CALCULATION")),
                    ts_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="TECHNICAL SPECIFICATION")),
                    tr_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="TECHNICAL REPORT")),
                    pr_approved = Count("id", filter=Q(is_approved=True, is_archive=False, manual_type="PROJECT REPORT")),
                )
                data = {
                    "manuals": manual["manuals_approved"] or 0,
                    "rb": manual["rb_approved"] or 0,
                    "td": manual["td_approved"] or 0,
                    "catalouge": manual["catalouge_approved"] or 0,
                    "tc": manual["tc_approved"] or 0,
                    "ts": manual["ts_approved"] or 0,
                    "tr": manual["tr_approved"] or 0,
                    "pr": manual["pr_approved"] or 0,
                }
            elif status_type == "Archived":
                manual = Manual.objects.select_related().aggregate(
                    manuals_archived = Count("id", filter=Q(is_archive=True, manual_type="MANUALS")),
                    rb_archived = Count("id", filter=Q(is_archive=True, manual_type="REFERENCE BOOK")),
                    td_archived = Count("id", filter=Q(is_archive=True, manual_type="TENDER DOCUMENT")),
                    catalouge_archived = Count("id", filter=Q(is_archive=True, manual_type="CATALOUGE")),
                    tc_archived = Count("id", filter=Q(is_archive=True, manual_type="TECHNICAL CALCULATION")),
                    ts_archived = Count("id", filter=Q(is_archive=True, manual_type="TECHNICAL SPECIFICATION")),
                    tr_archived = Count("id", filter=Q(is_archive=True, manual_type="TECHNICAL REPORT")),
                    pr_archived = Count("id", filter=Q(is_archive=True, manual_type="PROJECT REPORT")),
                )
                data = {
                    "manuals": manual["manuals_archived"] or 0,
                    "rb": manual["rb_archived"] or 0,
                    "td": manual["td_archived"] or 0,
                    "catalouge": manual["catalouge_archived"] or 0,
                    "tc": manual["tc_archived"] or 0,
                    "ts": manual["ts_archived"] or 0,
                    "tr": manual["tr_archived"] or 0,
                    "pr": manual["pr_archived"] or 0,
                }
            else:
                manual = Manual.objects.select_related().aggregate(
                    manuals_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="MANUALS")),
                    rb_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="REFERENCE BOOK")),
                    td_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="TENDER DOCUMENT")),
                    catalouge_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="CATALOUGE")),
                    tc_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="TECHNICAL CALCULATION")),
                    ts_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="TECHNICAL SPECIFICATION")),
                    tr_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="TECHNICAL REPORT")),
                    pr_pending = Count("id", filter=Q(is_approved=False, is_archive=False, manual_type="PROJECT REPORT")),
                )
                data = {
                    "manuals": manual["manuals_pending"] or 0,
                    "rb": manual["rb_pending"] or 0,
                    "td": manual["td_pending"] or 0,
                    "catalouge": manual["catalouge_pending"] or 0,
                    "tc": manual["tc_pending"] or 0,
                    "ts": manual["ts_pending"] or 0,
                    "tr": manual["tr_pending"] or 0,
                    "pr": manual["pr_pending"] or 0,
                }
            response = {
                "success": True,
                "message": f"Document {status_type} data.",
                "results": data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        