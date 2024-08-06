from django.db import transaction
from django.http import FileResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from AuthApp.pagination import CustomPagination
from AuthApp.models import Department, Unit, Subvolume
from django.db.models import Q, Sum, Count, F, Value
from django.db.models.functions import Concat
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from core.utility import (
    Syserror,
    extract_drawing_type_number,
    find_corresponding_dwg,
    exist_corresponding_tif_pdf,
    is_delete_drawing_file,
    check_duplicate_drawing,
    get_file_name_and_extension,
    validateDrawingPerm
)
import os
from datetime import datetime
from DrawingApp.serializers import (
    DrawingListSerializer,
    ArchiveDrawingListSerializer,
    DrawingDetailSerializer,
    DrawingDescriptionSerializer,
    DrawingLogListSerializer,
    SearchDrawingSerializer,
    DrawingLogExcelListSerializer,
    DrawingEditSerializer,
    DrawingPendingListSerializer
)
from DrawingApp.models import (
    Drawing,
    DrawingFile,
    DrawingDescription,
    DrawingLog,
    DRAWING_FILE_TYPE_CHOICE,
    DRAWING_SIZE_CHOICE,
    DRAWING_LOG_STATUS_CHOICE,
)
from AuthApp.customAuth import allowed_admin_user, allowed_superadmin
import zipfile
import io
from django.conf import settings
class DrawingSizeApiView(APIView):
    def get(self, request):
        try:
            drawing_size_list = [item[0] for item in DRAWING_SIZE_CHOICE]
            response = {
                "success": True,
                "message": "Drawing initial data retrieved ",
                "results": drawing_size_list,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

# Create your views here.
class DrawingApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingListSerializer
    def get(self, request, id=None):
        try:
            perms = request.user.drawing_permission
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                    instance = Drawing.objects.select_related('department', 'unit', 'sub_volume').get(filter_criteria)
                    if request.user.role == "User":
                        if instance.is_layout and not validateDrawingPerm(perms, 'view_layout'):
                            return Response({
                            "success": False,
                            "message": "Required View Layout Permission.",
                            "results": None,
                            }, status=400)
                        if not validateDrawingPerm(perms, instance.drawing_type.lower()):
                            return Response({
                                "success": False,
                                "message": "Required View  Permission.",
                                "results": None,
                            }, status=400)
                    
                except Drawing.DoesNotExist:
                    return Response({"success": False, "message": "Drawing does not exist"}, status=400)
                
                serializer = DrawingDetailSerializer(instance)
                return Response({
                    "success": True,
                    "message": "Drawing retrieved successfully",
                    "results": serializer.data,
                }, status=200)

            # Retrieving list of  objects according to filter_criteria
            filter_criteria = Q(is_archive=False)
            if request.user.role == "User":
                filter_criteria &= Q(is_approved=True)

            query_params = {
                'drawing_type': request.GET.get("drawing_type"),
                'work_order_number__icontains': request.GET.get("work_order_number"),
                'department__department_id': request.GET.get("department_id"),
                'unit__unit_id': request.GET.get("unit_id"),
            }
            isDistinct = False
            for param, value in query_params.items():
                if value:
                    filter_criteria &= Q(**{param: value})

            if dwg_status := request.GET.get("status"):
                filter_criteria &= Q(is_approved=(dwg_status == "Approved"))

            if file_present := request.GET.get("file_present"):
                filter_criteria &= Q(is_file_present=(file_present == "Present"))

            if description := request.GET.get("description"):
                filter_criteria &= Q(description__description__icontains = description)
                isDistinct = True
                
            if query := request.GET.get("query"):
                drawing_number_list = [part.strip() for part in query.split(',')]
                drawing_number_criteria = Q()
                for drawing_number in drawing_number_list:
                    drawing_number_criteria |= Q(drawing_number__istartswith=drawing_number)
                filter_criteria &= drawing_number_criteria

            if request.user.role == "User":
                if not any(query_params.values()) and not query and not dwg_status and not file_present:
                    return Response({"success": True, "results": [], "count": 0}, status=200)
            
                if query_params.get('drawing_type') and not validateDrawingPerm(perms, query_params.get('drawing_type').lower()):
                    return Response({
                            "success": False,
                            "message": "Required View  Permission.",
                            "results": None,
                        }, status=400)
            
            user_empyt_filter = list(query_params.values())[1:]
            user_empyt_filter.extend([query, description])
            if request.user.role == "User" and query_params.get("drawing_type", None) and not any(user_empyt_filter):
                return Response({"success": "True", "results": [], "count": 0}, status=200)
            
            if isDistinct:
                instance = Drawing.objects.select_related('department', 'unit', 'sub_volume').prefetch_related('files').filter(
                filter_criteria).annotate(description_count=Count('description', distinct=True)).order_by('drawing_number_numeric')
            else:
                instance = Drawing.objects.select_related('department', 'unit', 'sub_volume').prefetch_related('files').filter(filter_criteria).order_by('drawing_number_numeric')
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = DrawingListSerializer(instance, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            Syserror(e)
            return Response({"success": False, "message": str(e)}, status=400)
        
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            drawing_type = data.get("drawing_type", None) or None
            drawing_number = data.get("drawing_number", None) or None
            supplier_name = data.get("supplier_name", None) or None 
            vendor_number = data.get("vendor_number", None) or None
            client_number = data.get("client_number", None) or None
            package_number = data.get("package_number", None) or None
            work_order_number = data.get("work_order_number", None) or None
            drawing_size = data.get("drawing_size", None) or None
            drawing_file_type = data.get("drawing_file_type", None) or None
            is_layout = data.get("is_layout", "NO") == "YES"
            is_dwg_file_present = data.get("dwg_file", "NO") == "YES"
            date_of_registration = data.get("date_of_registration", None) or None
            certification = data.get("certification", "NOT CERTIFIED")
            remarks = data.get("remarks", None) or None
            no_of_sheet = data.get("no_of_sheet", None) or None
            description = data.get("description", [])
            volume = data.get("volume", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            pdr_number = data.get("pdr_number", None) or None
            letter_number = data.get("letter_number", None) or None  # letter number and date
            fdr_approved_date = data.get("fdr_approved_date", None) or None
            required_field = [
                drawing_type,
                remarks,
                drawing_number,
                drawing_size,
                drawing_file_type,
                no_of_sheet,
                description,
            ]
            if not all(required_field):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required.",
                }
                return Response(response, status=400)

            if drawing_type in ["PDR", "CDBR"]:
                volume = None
                try:
                    department = Department.objects.get(department_id=department)
                except:
                    response = {
                        "success": False,
                        "message": "Departemnt does not exist.",
                    }
                    return Response(response, status=400)
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit:
                    response = {"success": False, "message": "Unit does not exist."}
                    return Response(response, status=400)

            elif drawing_type == "RS":
                try:
                    volume = Subvolume.objects.get(sub_volume_no=volume)
                except:
                    response = {
                        "success": False,
                        "message": "Volume does not exist.",
                    }
                    return Response(response, status=400)
                department = None
                unit = None

            elif drawing_type == "PS":
                volume = None
                department = None
                unit = None

            elif drawing_type == "FDR":
                volume = None
                unit = None
                client_number = None
                work_order_number = None
                vendor_number = None
                date_of_registration = None
                if department:
                    try:
                        department = Department.objects.get(department_id=department)
                    except:
                        response = {
                            "success": False,
                            "message": "Departemnt does not exist.",
                        }
                        return Response(response, status=400)

            elif drawing_type == "MISC":
                volume = None
                client_number = None
                work_order_number = None
                vendor_number = None
                date_of_registration = None
                package_number = None
                if department:
                    try:
                        department = Department.objects.get(department_id=department)
                    except:
                        response = {
                            "success": False,
                            "message": "Departemnt does not exist.",
                        }
                        return Response(response, status=400)
                else:
                    department = None

                if unit:
                    try:
                        unit = Unit.objects.get(unit_id=unit)
                    except:
                        response = {"success": False, "message": "Unit does not exist."}
                        return Response(response, status=400)
                else:
                    unit = None
            else:
                response = {
                    "success": False,
                    "message": "Invalid drawing type.",
                }
                return Response(response, status=400)

            if all(drawing_file_type != item[0] for item in DRAWING_FILE_TYPE_CHOICE):
                response = {"success": False, "message": "Invalid file type ."}
                return Response(response, status=400)

            if all(drawing_size != item[0] for item in DRAWING_SIZE_CHOICE):
                response = {"success": False, "message": "Invalid drawing size."}
                return Response(response, status=400)
            if drawing_type not in ["RS", "MISC"]:
                if not drawing_number.isdigit() or int(drawing_number) < 1:
                    response = {
                        "success": False,
                        "message": "Invalid drawing number. Required only digits",
                    }
                    return Response(response, status=400)

            if not isinstance(no_of_sheet, int) or no_of_sheet < 1:
                response = {
                    "success": False,
                    "message": "Invalid number of sheet",
                }
                return Response(response, status=400)

            if (
                not isinstance(description, list)
                or len(description) != no_of_sheet
                or not all(description)
            ):
                response = {
                    "success": False,
                    "message": "Number of description not matched with number of sheets",
                }
                return Response(response, status=400)
            
            if drawing_type in ["PDR", "CDBR", "PS", "RS"]:
                fdr_approved_date = None
                pdr_number = None
                letter_number = None
                try:
                    date_of_registration = datetime.strptime(date_of_registration, "%Y-%m-%d").date()
                except:
                    response = {
                            "success": False,
                            "message": f"Invalid Date of Registration format {date_of_registration}.",
                        }
                    return Response(response, status=400)
            elif drawing_type == "FDR":
                if fdr_approved_date:
                    try:
                        fdr_approved_date = datetime.strptime(fdr_approved_date, "%Y-%m-%d").date()
                    except:
                        response = {
                            "success": False,
                            "message": f"Invalid approved date format {fdr_approved_date}.",
                        }
                        return Response(response, status=400)
                else:
                    fdr_approved_date = None
            else:
                fdr_approved_date = None
                pdr_number = None
                letter_number = None

            if Drawing.objects.filter(drawing_number=drawing_number, drawing_type=drawing_type).exists():
                response = {
                    "success": False,
                    "message": "Drawing number already exist.",
                }
                return Response(response, status=400)

            with transaction.atomic():
                instance = Drawing.objects.create(
                    drawing_type=drawing_type,
                    drawing_number=drawing_number,
                    supplier_name=supplier_name,
                    vendor_number=vendor_number,
                    client_number=client_number,
                    package_number=package_number,
                    drawing_size=drawing_size,
                    drawing_file_type=drawing_file_type,
                    is_layout=is_layout,
                    work_order_number=work_order_number,
                    is_dwg_file_present=is_dwg_file_present,
                    date_of_registration=date_of_registration,
                    certification=certification,
                    no_of_sheet=no_of_sheet,
                    sub_volume=volume,
                    department=department,
                    unit=unit,
                    remarks=remarks,
                    uploaded_by=request.user,
                    letter_number=letter_number,
                    fdr_approved_date=fdr_approved_date or None,
                    pdr_number=pdr_number,
                )
                for index, item in enumerate(description, start=1):
                    if index == 1:
                        instance.default_description = item
                        instance.save()
                    DrawingDescription.objects.create(
                        index=index, drawing=instance, description=item
                    )
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=instance,
                    status="Add Drawing",
                    message="Drawing added",
                    details=f"add drawing data",
                )
                response = {
                    "success": True,
                    "message": "Drawing created  successfully.",
                    "results": {
                        "id": instance.id,
                        "drawing_number": instance.drawing_number,
                        "drawing_type": instance.drawing_type,
                        "drawing_file_type": instance.drawing_file_type,
                        "no_of_sheet": instance.no_of_sheet,
                        "is_dwg_file_present": instance.is_dwg_file_present,
                    },
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class DrawingEditApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingEditSerializer

    def get(self, request, id=None):
        try:
            # retrive single object of user model
            if id:
                try:
                    filter_criteria = Q(id=id)
                    if request.user.role == "User":
                        filter_criteria &= Q(is_archive=False, is_approved=True)
                    instance = Drawing.objects.get(filter_criteria)
                except Drawing.DoesNotExist:
                    response = {"success": False, "message": "Drawing does not exist"}
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Drawing retrieved successfully",
                    "results": serializer.data,
                }
                return Response(response, status=200)

            response = {"success": False, "message": "Required drawing id"}
            return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request, id):
        try:
            data = request.data
            work_order_number = data.get("work_order_number", None) or None
            supplier_name = data.get("supplier_name", None) or None
            vendor_number = data.get("vendor_number", None) or None
            client_number = data.get("client_number", None) or None
            package_number = data.get("package_number", None) or None
            drawing_size = data.get("drawing_size", None) or None
            drawing_file_type = data.get("drawing_file_type", None) or None
            revision_version = data.get("revision", None) or None
            is_layout = data.get("is_layout", "NO") == "YES"
            is_dwg_file_present = data.get("dwg_file", "NO") == "YES"
            certification = data.get("certification", "NOT CERTIFIED") or None
            remarks = data.get("remarks", None)
            no_of_sheet = data.get("no_of_sheet", None)
            description = data.get("description", [])
            volume = data.get("volume", None) or None
            department = data.get("department_id", None) or None
            unit = data.get("unit_id", None) or None
            pdr_number = data.get("pdr_number", None) or None
            letter_number = data.get("letter_number", None) or None  # letter number and date
            fdr_approved_date = data.get("fdr_approved_date", None) or None
            required_field = [
                remarks,
                drawing_size,
                drawing_file_type,
                no_of_sheet,
                description,
                revision_version,
            ]
            if not all(required_field):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required.",
                }
                return Response(response, status=400)
            try:
                drawing = Drawing.objects.get(id=id)
            except:
                response = {"success": False, "message": "Drawing does not exist."}
                return Response(response, status=400)

            if drawing.drawing_type in ["PDR", "CDBR"]:
                volume = None
                try:
                    department = Department.objects.get(department_id=department)
                except Department.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Departemnt does not exist.",
                    }
                    return Response(response, status=400)
                try:
                    unit = Unit.objects.get(unit_id=unit)
                except Unit.DoesNotExist:
                    response = {"success": False, "message": "Unit does not exist."}
                    return Response(response, status=400)

            elif drawing.drawing_type == "RS":
                try:
                    volume = Subvolume.objects.get(sub_volume_no=volume)
                except Subvolume.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Volume does not exist.",
                    }
                    return Response(response, status=400)
                department = None
                unit = None
            elif drawing.drawing_type == "PS":
                volume = None
                department = None
                unit = None
            elif drawing.drawing_type == "FDR":
                volume = None
                unit = None
                client_number = None
                work_order_number = None
                vendor_number = None
                if department:
                    try:
                        department = Department.objects.get(department_id=department)
                    except:
                        response = {
                            "success": False,
                            "message": "Departemnt does not exist.",
                        }
                        return Response(response, status=400)

            elif drawing.drawing_type == "MISC":
                volume = None
                client_number = None
                work_order_number = None
                vendor_number = None
                package_number = None
                if department:
                    try:
                        department = Department.objects.get(department_id=department)
                    except:
                        response = {
                            "success": False,
                            "message": "Departemnt does not exist.",
                        }
                        return Response(response, status=400)
                else:
                    department = None

                if unit:
                    try:
                        unit = Unit.objects.get(unit_id=unit)
                    except:
                        response = {"success": False, "message": "Unit does not exist."}
                        return Response(response, status=400)
                else:
                    unit = None
            else:
                response = {
                    "success": False,
                    "message": "Invalid drawing type.",
                }
                return Response(response, status=400)

            if all(drawing_file_type != item[0] for item in DRAWING_FILE_TYPE_CHOICE):
                response = {"success": False, "message": "Invalid file type ."}
                return Response(response, status=400)

            if all(drawing_size != item[0] for item in DRAWING_SIZE_CHOICE):
                response = {"success": False, "message": "Invalid drawing size."}
                return Response(response, status=400)

            if not isinstance(no_of_sheet, int) or no_of_sheet < 1:
                response = {
                    "success": False,
                    "message": "Invalid number of sheet",
                }
                return Response(response, status=400)

            if not str(revision_version).isdigit() :
                response = {
                    "success": False,
                    "message": "Invalid revision",
                }
                return Response(response, status=400)

            if (
                not isinstance(description, list)
                or len(description) != no_of_sheet
                or not all(description)
            ):
                response = {
                    "success": False,
                    "message": "Number of description does not matched with number of sheets",
                }
                return Response(response, status=400)
            old_no_of_sheet = drawing.no_of_sheet
            log_details = ""
            is_file_type_change = False
            with transaction.atomic():
                if drawing.work_order_number != work_order_number:
                    log_details += f"Work Order No.: {drawing.work_order_number} ➡️ {work_order_number} |"
                    drawing.work_order_number = work_order_number

                if drawing.supplier_name != supplier_name:
                    log_details += (
                        f"Supplier: {drawing.supplier_name} ➡️ {supplier_name} |"
                    )
                    drawing.supplier_name = supplier_name

                if drawing.vendor_number != vendor_number:
                    log_details += (
                        f"Vendor No: {drawing.vendor_number} ➡️ {vendor_number} |"
                    )
                    drawing.vendor_number = vendor_number

                if drawing.client_number != client_number:
                    log_details += (
                        f"Client No: {drawing.client_number} ➡️ {client_number} |"
                    )
                    drawing.client_number = client_number

                if drawing.package_number != package_number:
                    log_details += (
                        f"Package No: {drawing.package_number} ➡️ {package_number} |"
                    )
                    drawing.package_number = package_number

                if drawing.drawing_size != drawing_size:
                    log_details += (
                        f"Size of Drawing: {drawing.drawing_size} ➡️ {drawing_size} |"
                    )
                    drawing.drawing_size = drawing_size

                if drawing.drawing_file_type != drawing_file_type:
                    log_details += f"Drawing File Type: {drawing.drawing_file_type} ➡️ {drawing_file_type} |"
                    drawing.drawing_file_type = drawing_file_type
                    is_file_type_change = True

                if drawing.revision_version != revision_version:
                    log_details += (
                        f"Revision: {drawing.revision_version} ➡️ {revision_version} |"
                    )
                    drawing.revision_version = revision_version

                if drawing.is_layout != is_layout:
                    log_details += f"Layout: {'YES' if drawing.is_layout else 'NO'} ➡️ {'YES' if is_layout else 'NO'} |"
                    drawing.is_layout = is_layout

                if drawing.is_dwg_file_present != is_dwg_file_present:
                    log_details += f"DWG File. {'YES' if drawing.is_dwg_file_present else 'NO'} ➡️ {'YES' if is_dwg_file_present else 'NO'} |"
                    drawing.is_dwg_file_present = is_dwg_file_present

                if drawing.certification != certification:
                    log_details += (
                        f"Certification: {drawing.certification} ➡️ {certification} |"
                    )
                    drawing.certification = certification

                if drawing.no_of_sheet != no_of_sheet:
                    log_details += (
                        f"Number of Sheet: {drawing.no_of_sheet} ➡️ {no_of_sheet} |"
                    )
                    drawing.no_of_sheet = no_of_sheet

                if drawing.sub_volume != volume:
                    log_details += f"Volume: {drawing.sub_volume.name if drawing.sub_volume else None} ➡️ {volume.name if volume else None} |"
                    drawing.sub_volume = volume

                if drawing.department != department:
                    log_details += f"Department: {drawing.department.name if drawing.department else None} ➡️ {department.name if department else None} |"
                    drawing.department = department

                if drawing.unit != unit:
                    log_details += f"Unit: {drawing.unit.name if drawing.unit else None} ➡️ {unit.name if unit else None} |"
                    drawing.unit = unit

                if drawing.remarks != remarks:
                    log_details += f"Remarks: {drawing.remarks} ➡️ {remarks} |"
                    drawing.remarks = remarks

                if drawing.pdr_number != pdr_number:
                    log_details += f"PDR Number.: {drawing.pdr_number} ➡️ {pdr_number} |"
                    drawing.pdr_number = pdr_number

                if drawing.letter_number != letter_number:
                    log_details += f"Letter No & Date.: {drawing.letter_number} ➡️ {letter_number} |"
                    drawing.letter_number = letter_number
                if fdr_approved_date:
                    try:
                        fdr_approved_date = datetime.strptime(
                            fdr_approved_date, "%Y-%m-%d"
                        ).date()
                    except:
                        response = {
                            "success": False,
                            "message": "Invalid Approved Date Format",
                        }
                        return Response(response, status=400)
                    if drawing.fdr_approved_date != fdr_approved_date:
                        log_details += f"Approved Date.: {drawing.fdr_approved_date} ➡️ {fdr_approved_date} |"
                        drawing.fdr_approved_date = fdr_approved_date
                is_any_file_deleted = False
                is_delete_file = is_delete_drawing_file(old_no_of_sheet, no_of_sheet)
                updated_desc_id_list = []
                for index, item in enumerate(description, start=1):
                    des_text = item.get("description", None)
                    desc_id = item.get("id", None)
                    if desc_id:
                        if descexist := DrawingDescription.objects.filter(
                            drawing=drawing, id=desc_id
                        ):
                            desc = descexist.first()
                            if desc.drawing_file:
                                if desc.index != index or is_delete_file:
                                    desc.drawing_file.delete()
                                    desc.drawing_file = None
                                    is_any_file_deleted = True

                            desc.index = index
                            if desc.description != des_text:
                                log_details += f"Description-{index}: {desc.description} ➡️ {des_text} |"
                                desc.description = des_text
                            desc.save()
                        else:
                            raise ValueError(
                                f"Description with index {index}, got invalid ID"
                            )
                    else:
                        desc = DrawingDescription.objects.create(
                            index=index, drawing=drawing, description=des_text
                        )
                        log_details += f"Description-{index}: {des_text} ➕|"

                    if index == 1:
                        drawing.default_description = des_text
                    updated_desc_id_list.append(desc.id)

                deleted_description = DrawingDescription.objects.filter(drawing=drawing).exclude(id__in=updated_desc_id_list)

                for desc in deleted_description:
                    if desc.drawing_file:
                        desc.drawing_file.delete()
                    log_details += f"Description: {desc.description} ❌|"
                    desc.delete()

                if is_file_type_change:
                    for file in DrawingFile.objects.filter(drawing = drawing):
                        log_details += f"Drawing File Deleted: {file.file_name} ❌|"
                        file.delete()

                if is_any_file_deleted or is_file_type_change:
                    drawing.is_file_present = False
                    drawing.is_approved = False
                    drawing.approved_by = None
                drawing.save()
                if log_details:
                    DrawingLog.objects.create(
                        user=request.user,
                        drawing=drawing,
                        status="Update Drawing",
                        message="drawing updated",
                        details=log_details,
                    )
                response = {
                    "success": True,
                    "message": "Drawing updated successfully.",
                    "results": {
                        "id": drawing.id,
                        "drawing_number": drawing.drawing_number,
                        "drawing_type": drawing.drawing_type,
                        "drawing_file_type": drawing.drawing_file_type,
                        "no_of_sheet": drawing.no_of_sheet,
                        "is_dwg_file_present": drawing.is_dwg_file_present,
                    },
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UploadDrawingFileApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingDescriptionSerializer

    # upload new file only
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            file_list = data.getlist("file_list", [])
            drawing_id = data.get("drawing_id", None)
            if not drawing_id:
                response = {"success": False, "message": "Required Drawing ID"}
                return Response(response, status=400)

            try:
                drawing = Drawing.objects.get(id=drawing_id)
            except Drawing.DoesNotExist:
                response = {"success": False, "message": "Drawing does not exist."}
                return Response(response, status=400)

            if not file_list:
                response = {"success": False, "message": "required files."}
                return Response(response, status=400)

            is_file_list_valid = all(
                isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                for file in file_list
            )
            # validate all the file must be instance InMemoryUploadedFile or UploadedFile that means file_list var have file_list value is file
            if not is_file_list_valid:
                response = {"success": False, "message": "Upload valid files."}
                return Response(response, status=400)

            # valid all the file that have accurate file extension name same with drwaing file type
            allowed_file_type = ["TIF", "TIFF"] if drawing.drawing_file_type == "TIF" else ["PDF"]
            if drawing.is_dwg_file_present:
                allowed_file_type.append("DWG")
            
            if drawing.no_of_sheet > 1:
                actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}SH{i}" for i in range(1, drawing.no_of_sheet + 1)]
            else:
                actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}"]

            for file in file_list:
                file_name, file_ext = get_file_name_and_extension(file.name)

                if file_ext not in allowed_file_type:
                    raise ValueError(f"Wrong file extension {file.name}")
                
                if file_name not in actual_file_name_list:
                    raise ValueError(f"Invalid file name {file.name}")
            # loop end

            if drawing.is_dwg_file_present:
                same_name_dwg_files = []
                all_files = []
                for file in file_list:
                    file_name, extension = get_file_name_and_extension(file.name)
                    if extension == "DWG":
                        if exist_corresponding_tif_pdf(file_name, file_list):
                            same_name_dwg_files.append(file)
                    else:
                        all_files.append(file)
            else:
                same_name_dwg_files = []
                all_files = file_list

            with transaction.atomic():
                log_details = ""
                for file in all_files:
                    dwg_file = None
                    file_name, file_ext = get_file_name_and_extension(file.name)
                    if drawing.is_dwg_file_present and file_ext != "DWG":
                        # if any file like pdf of tif get it corresponding .dwg file
                        dwg_file = find_corresponding_dwg(file_name, same_name_dwg_files)
                    if not DrawingFile.objects.filter(drawing=drawing, file_name=file_name).exists():
                        DrawingFile.objects.create(drawing=drawing, file=file, dwg_file=dwg_file)
                        log_details += f"add new file: {file.name}"

                if drawing.no_of_sheet == drawing.files.count():
                    drawing.is_file_present = True
                    if request.user.is_superuser:
                        drawing.is_approved = True
                        drawing.approved_by = request.user
                else:
                    drawing.is_file_present = False
                    drawing.approved_by = None
                    drawing.is_approved = False

                drawing.save()

                # create log
                if log_details:
                    DrawingLog.objects.create(
                        user=request.user,
                        drawing=drawing,
                        status="Add Drawing",
                        message="drawing file added",
                        details=log_details,
                    )

                response = {
                    "success": True,
                    "message": "Drawing file upload successfully.",
                    "results": drawing.id,
                }
                return Response(response, status=200)

        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    # upload update as well as new file
    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            file_list = data.getlist("file_list", [])
            drawing_id = data.get("drawing_id", None)
            replacefile = data.get("replacefile", "NO") == "YES"
            if not drawing_id:
                response = {"success": False, "message": "Required Drawing ID"}
                return Response(response, status=400)

            try:
                drawing = Drawing.objects.get(id=drawing_id)
            except Drawing.DoesNotExist:
                response = {"success": False, "message": "Drawing does not exist."}
                return Response(response, status=400)

            if not file_list:
                response = {"success": False, "message": "required files."}
                return Response(response, status=400)

            is_file_list_valid = all(
                isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                for file in file_list
            )
            # validate all the file must be instance InMemoryUploadedFile or UploadedFile that means file_list var have file_list value is file
            if not is_file_list_valid:
                response = {"success": False, "message": "Upload valid files."}
                return Response(response, status=400)

            # valid all the file that have accurate file extension name same with drwaing file type
            allowed_file_type = ["TIF", "TIFF"] if drawing.drawing_file_type == "TIF" else ["PDF"]
            if drawing.is_dwg_file_present:
                allowed_file_type.append("DWG")
            
            if drawing.no_of_sheet > 1:
                actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}SH{i}" for i in range(1, drawing.no_of_sheet + 1)]
            else:
                actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}"]

            for file in file_list:
                file_name, file_ext = get_file_name_and_extension(file.name)
                if file_ext not in allowed_file_type:
                    raise ValueError(f"Wrong file extension {file.name}")

                if file_name not in actual_file_name_list:
                    raise ValueError(f"Invalid file name {file.name}")
            # loop end
            if drawing.is_dwg_file_present:
                same_name_dwg_files = []
                all_files = []
                for file in file_list:
                    file_name, extension = get_file_name_and_extension(file.name)
                    if extension == "DWG":
                        if exist_corresponding_tif_pdf(file_name, file_list):
                            same_name_dwg_files.append(file)
                        else:
                            all_files.append(file)
                    else:
                        all_files.append(file)
            else:
                same_name_dwg_files = []
                all_files = file_list

            with transaction.atomic():
                log_details = ""
                for file in all_files:
                    dwg_file = None
                    file_name, file_ext = get_file_name_and_extension(file.name)
                    if drawing.is_dwg_file_present and file_ext != "DWG":
                        dwg_file = find_corresponding_dwg(file_name, same_name_dwg_files)
                    if old_drawing_file := DrawingFile.objects.filter(drawing=drawing, file_name=file_name):  
                        old_drawingfile = old_drawing_file.first()
                        if file_ext != "DWG":
                            if replacefile:
                                old_drawingfile.delete()
                                # when create new drawing the core file not be .dwg file
                                DrawingFile.objects.create(drawing=drawing, file=file, dwg_file=dwg_file)
                                log_details += f"add updated file. {file.name}"

                        elif not old_drawingfile.dwg_file:
                            old_drawingfile.dwg_file = file
                            old_drawingfile.save()
                            log_details += f"add new file. {file.name}"

                        elif old_drawingfile.dwg_file and replacefile:
                            old_dwg_path = old_drawingfile.dwg_file.path
                            if os.path.isfile(old_dwg_path):
                                os.remove(old_dwg_path)
                            old_drawingfile.dwg_file = file
                            old_drawingfile.save()
                            log_details += f"add updated file. {file.name}"

                    elif file_ext != "DWG":
                        # when create new drawing the core file not be .dwg file
                        DrawingFile.objects.create(drawing=drawing, file=file, dwg_file=dwg_file)
                        log_details += f"add new file. {file.name}"
                    

                if drawing.no_of_sheet == drawing.files.count():
                    drawing.is_file_present = True
                    if request.user.is_superuser:
                        drawing.is_approved = True
                        drawing.approved_by = request.user
                    elif replacefile:  # let approved it again
                        drawing.is_approved = False
                        drawing.approved_by = None
                else:
                    drawing.is_file_present = False
                    drawing.approved_by = None
                    drawing.is_approved = False

                drawing.save()

                # create log
                if log_details:
                    DrawingLog.objects.create(
                        user=request.user,
                        drawing=drawing,
                        status="Update Drawing" if replacefile else "Add Drawing",
                        message=(
                            "revised drawing file updated"
                            if replacefile
                            else "new drawing file added"
                        ),
                        details=log_details,
                    )

                descriptionList = (
                    DrawingDescription.objects.select_related()
                    .filter(drawing=drawing)
                    .order_by("index")
                )
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(descriptionList, request, view=self)
                response_data = {}
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    response_data.update(result.data)

                response_data.update(
                    {
                        "success": True,
                        "message": "Revised drawing file uploaded successfully.",
                    }
                )
                return Response(response_data, status=200)

        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class ApproveDrawingApiView(APIView):  # for pending drawing
    #pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingPendingListSerializer
    @allowed_superadmin
    def get(self, request):
        instance = (
            Drawing.objects.select_related('department', 'unit', 'sub_volume').prefetch_related('files')
            .filter(is_archive=False, is_approved=False)
            .order_by("drawing_number_numeric")
        )
        # paginator = self.pagination_class()
        # page = paginator.paginate_queryset(instance, request, view=self)
        # if page is not None:
        #     serializer = self.serializer_class(page, many=True)
        #     return paginator.get_paginated_response(serializer.data)

        serializer = DrawingListSerializer(instance, many=True)
        return Response({
            "success": True,
            "message": "Pending Drawing List",
            "results": serializer.data,
            }, status=200)

    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            drawing_id = data.get("id", None)
            if not drawing_id:
                response = {"success": False, "message": "Required drawing ID"}
                return Response(response, status=400)
            try:
                drawing = Drawing.objects.get(id=drawing_id, is_archive=False)
            except Drawing.DoesNotExist:
                response = {"success": False, "message": "Drawing doesn't exist."}
                return Response(response, status=400)

            if drawing.is_file_present:
                drawing.is_approved = True
                drawing.save()
                response = {
                    "success": True,
                    "message": "Drawing approved successfully.",
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Drawing's all file not present",
                }
                return Response(response, status=400)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            drawing_id_list = data.get("drawing_id_list", [])
            if not drawing_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one drawing ID",
                }
                return Response(response, status=400)

            Drawing.objects.filter(id__in=drawing_id_list, is_archive=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "Drawing approved successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class ArchiveDrawingApiView(APIView):
    serializer_class = ArchiveDrawingListSerializer

    @allowed_superadmin
    def get(self, request):
        try:
            # retrive list of drawing object according to filter_criteria
            filter_criteria = Q(is_archive=True)
            if drawing_type := request.GET.get("drawing_type"):
                filter_criteria &= Q(drawing_type=drawing_type)

            if work_order_number := request.GET.get("work_order_number"):
                filter_criteria &= Q(work_order_number__icontains=work_order_number)

            if description := request.GET.get("description"):
                filter_criteria &= Q(description__description__icontains=description)

            if department_id := request.GET.get("department_id"):
                filter_criteria &= Q(department__department_id=department_id)

            if unit_id := request.GET.get("unit_id"):
                filter_criteria &= Q(unit__unit_id=unit_id)

            if query := request.GET.get("query"):
                drawing_type, drawing_number = extract_drawing_type_number(
                    query.upper()
                )
                if drawing_type:
                    if drawing_number:
                        filter_criteria &= Q(
                            Q(drawing_type=drawing_type),
                            Q(drawing_number__icontains=drawing_number),
                        )
                    else:
                        filter_criteria &= Q(drawing_type=drawing_type)
                else:
                    filter_criteria &= Q(
                        Q(drawing_type__icontains=query)
                        | Q(drawing_file_type__icontains=query)
                        | Q(drawing_number__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(department__department_id__icontains=query)
                        | Q(unit__name__icontains=query)
                        | Q(unit__unit_id__icontains=query)
                        | Q(remarks__icontains=query)
                        | Q(description__description__icontains=query)
                    )
            instance = (
                Drawing.objects.select_related()
                .filter(filter_criteria)
                .order_by("-created_at").distinct()
            )

            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve archived drawing successfully.",
                "results": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            drawing_id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)
            if not drawing_id:
                response = {"success": False, "message": "Required drawing ID"}
                return Response(response, status=400)
            try:
                drawing = Drawing.objects.get(id=drawing_id)
            except Drawing.DoesNotExist:
                response = {"success": False, "message": "Drawing doesn't exist."}
                return Response(response, status=400)
            
            if is_archive:
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=drawing,
                    status="Archive Drawing",
                    message="Drawing archived",
                    details=f"archive reason : {archive_reason}",
                )
            else:
                archive_reason = None
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=drawing,
                    status="Update Drawing",
                    message="Drawing unarchived",
                    details=f"archive reason : {drawing.archive_reason} ➡️ None",
                )

            drawing.is_archive = is_archive
            drawing.archive_reason = archive_reason
            drawing.save()
            response = {
                "success": True,
                "message": f'Drawing {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    # unarchived drawing
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            drawing_list = data.get("drawing_list", [])
            if not drawing_list:
                response = {"success": False, "message": "Required drawing list"}
                return Response(response, status=400)

            for drawing in Drawing.objects.filter(id__in=drawing_list, is_archive=True):
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=drawing,
                    status="Update Drawing",
                    message="Drawing unarchived",
                    details=f"archive reason : {drawing.archive_reason} ➡️ None",
                )
                drawing.is_archive=False
                drawing.archive_reason=None
                drawing.save()
            response = {
                "success": True,
                "message": "Drawings unarchive successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class DrawingPermanentDeleteApiView(APIView):

    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            drawing_list = data.get("drawing_list", [])
            if not drawing_list:
                response = {"success": False, "message": "Required drawing list"}
                return Response(response, status=400)

            drawings = Drawing.objects.filter(id__in=drawing_list, is_archive=True)
            for i in drawings:
                for desc in i.description.all():
                    if desc.drawing_file:
                        desc.drawing_file.delete()
                    desc.delete()
                i.drawinglog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.drawing_type}-{i.drawing_number} DELETED)"),)
                    ).update(message=F("new_message"))
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=None,
                    status="Delete Drawing",
                    message=f"Drawing Deleted ({i.drawing_type}-{i.drawing_number})",
                    details=f"Drawing {i.drawing_type}-{i.drawing_number} DELETED.",
                )
                i.delete()
            response = {
                "success": True,
                "message": "Drawings permanently deleted successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class BulkUploadDrawingApiView(APIView):
    serializer_class = DrawingListSerializer

    # upload drawing data   
    @allowed_admin_user
    def post(self, request):
        try:
            data_list = request.data.get("data_list", [])
            if not isinstance(data_list, list) or len(data_list) == 0:
                response = {
                    "success": False,
                    "message": "Required alteast one data set.",
                }
                return Response(response, status=400)
            new_data_list = []
            error_data_set = []
            for index, data in enumerate(data_list, start=2):
                drawing_type = data.get("drawing_type", None)
                drawing_number = data.get("drawing_number", None)
                drawing_file_type = data.get("drawing_file_type", None)
                supplier_name = data.get("supplier_name", None)
                vendor_number = data.get("vendor_number", None)
                client_number = data.get("client_number", None)
                package_number = data.get("package_number", None)
                drawing_size = data.get("drawing_size", None)
                is_layout = data.get("is_layout", "NO") == "YES"
                is_dwg_file_present = data.get("dwg_file", "NO") == "YES"
                date_of_registration = data.get("date_of_registration", None)
                certification = data.get("certification", "certified")
                remarks = data.get("remarks", None)
                revision = data.get("revision", 0)
                no_of_sheet = data.get("no_of_sheet", None)
                description = data.get("description", [])
                volume = data.get("volume_no", None)
                department = data.get("department_id", None)
                unit = data.get("unit_id", None)
                work_order_number = data.get("work_order_number", None)
                pdr_number = data.get("pdr_number", None)
                letter_number = data.get("letter_number_date", None)
                approved_date = data.get("approved_date", None)

                required_field = [
                    drawing_type,
                    remarks,
                    drawing_number,
                    drawing_size,
                    drawing_file_type,
                    no_of_sheet,
                    description,
                ]
                if not all(required_field):
                    error_data_set.append(
                        {"row": index, "message": "All the mandatory fields are required."}
                    )
                    continue
                
                if check_duplicate_drawing(data_list, drawing_type, drawing_number):
                    error_data_set.append({"row": index, "message": f"Duplicate drwaing number {drawing_number} type {drawing_type} ."})
                    continue

                if drawing_type in ["PDR", "CDBR"]:
                    volume = None
                    try:
                        if not isinstance(department, int):
                            error_data_set.append({"row": index,"message": f"Departemnt Id {department} required Number"})
                        department = Department.objects.get(department_id=department)
                    except:
                        error_data_set.append({"row": index,"message": f"Departemnt Id {department} does not exist."})
                        continue
                    try:
                        if not isinstance(unit, int):
                            error_data_set.append(
                                {
                                    "row": index,
                                    "message": f"Unit Id {unit} required Number",
                                }
                            )
                        unit = Unit.objects.get(unit_id=unit)
                    except:
                        error_data_set.append(
                            {"row": index, "message": f"Unit Id {unit} does not exist."}
                        )
                        continue

                elif drawing_type == "RS":
                    try:
                        volume = Subvolume.objects.get(sub_volume_no=volume)
                    except:
                        error_data_set.append(
                            {
                                "row": index,
                                "message": f"Volume no {volume} does not exist.",
                            }
                        )
                        continue
                    department = None
                    unit = None
                
                elif drawing_type == "PS":
                    volume = None
                    department = None
                    unit = None
                
                elif drawing_type == "FDR":
                    volume = None
                    unit = None
                    client_number = None
                    work_order_number = None
                    vendor_number = None
                    date_of_registration = None
                    if department:
                        try:
                            department = Department.objects.get(department_id=department)
                        except:
                            error_data_set.append({"row": index,"message": f"Department id {department} does not exist."})
                            continue
            
                elif drawing_type == "MISC":
                    volume = None
                    client_number = None
                    work_order_number = None
                    vendor_number = None
                    date_of_registration = None
                    package_number = None
                    if department:
                        try:
                            department = Department.objects.get(department_id=department)
                        except:
                            error_data_set.append({"row": index,"message": f"Department id {department} does not exist."})
                            continue
                    else:
                        department = None

                    if unit:
                        try:
                            unit = Unit.objects.get(unit_id=unit)
                        except:
                            error_data_set.append({"row": index,"message": f"Unit id {unit} does not exist."})
                            continue
                    else:
                        unit = None
                
                else:
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Invalid drawing type {drawing_type}.",
                        }
                    )
                    continue

                if all(drawing_file_type != item[0] for item in DRAWING_FILE_TYPE_CHOICE):
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Invalid drawing file type {drawing_file_type}.",
                        }
                    )
                    continue

                if all(drawing_size != item[0] for item in DRAWING_SIZE_CHOICE):
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Invalid drawing size. {drawing_size}",
                        }
                    )
                    continue
                
                if drawing_type not in ["RS", "MISC"]:
                    if not str(drawing_number).isdigit() or int(drawing_number) < 1:
                        error_data_set.append(
                            {
                                "row": index,
                                "message": f"Invalid drawing number {drawing_number}",
                            }
                        )
                        continue

                if not isinstance(no_of_sheet, int) or no_of_sheet < 1:
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Invalid number of sheet {no_of_sheet}",
                        }
                    )
                    continue
                if not isinstance(revision, int) or no_of_sheet < 0:
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Invalid revision {revision}",
                        }
                    )
                    continue

                if not isinstance(description, list) and not all(description):
                    error_data_set.append({"row": index, "message": "got Empty description"})
                    continue

                if Drawing.objects.filter(
                    drawing_number=drawing_number, drawing_type=drawing_type
                ).exists():
                    error_data_set.append(
                        {
                            "row": index,
                            "message": f"Drawing number {drawing_number} with Type {drawing_type} already exist.",
                        }
                    )
                    continue
                if drawing_type in ["PDR", "CDBR", "PS", "RS"]:
                    approved_date = None
                    pdr_number = None
                    letter_number = None
                    try:
                        date_of_registration = datetime.strptime(date_of_registration, "%Y-%m-%d").date()
                    except:
                        error_data_set.append(
                            {"row": index,"message": f"Invalid Date of Registration format {date_of_registration}.",}
                        )
                        continue
                elif drawing_type == "FDR":
                    if approved_date:
                        try:
                            approved_date = datetime.strptime(approved_date, "%Y-%m-%d").date()
                        except:
                            error_data_set.append(
                                {"row": index,"message": f"Invalid approved date format {approved_date}.",}
                            )
                            continue
                    else:
                        approved_date = None
                else:
                    approved_date = None
                    pdr_number = None
                    letter_number = None
                        

                new_data_list.append(
                    {
                        "drawing_type": drawing_type,
                        "drawing_number": drawing_number,
                        "drawing_file_type": drawing_file_type,
                        "supplier_name": supplier_name,
                        "vendor_number": vendor_number,
                        "client_number": client_number,
                        "package_number": package_number,
                        "drawing_size": drawing_size,
                        "is_layout": is_layout,
                        "is_dwg_file_present": is_dwg_file_present,
                        "date_of_registration": date_of_registration,
                        "certification": certification,
                        "remarks": remarks,
                        "no_of_sheet": no_of_sheet,
                        "description": description,
                        "volume": volume,
                        "department": department,
                        "revision": revision,
                        "unit": unit,
                        "work_order_number":work_order_number,
                        "pdr_number":pdr_number,
                        "letter_number":letter_number,
                        "approved_date":approved_date
                    })

            # validation end

            # create data start
            if not error_data_set:
                with transaction.atomic():
                    for data in new_data_list:
                        drawing_type = data.get("drawing_type")
                        drawing_number = data.get("drawing_number")
                        drawing_file_type = data.get("drawing_file_type")
                        supplier_name = data.get("supplier_name")
                        vendor_number = data.get("vendor_number")
                        client_number = data.get("client_number")
                        package_number = data.get("package_number")
                        drawing_size = data.get("drawing_size")
                        is_layout = data.get("is_layout")
                        is_dwg_file_present = data.get("is_dwg_file_present")
                        date_of_registration = data.get("date_of_registration")
                        certification = data.get("certification", None)
                        remarks = data.get("remarks")
                        no_of_sheet = data.get("no_of_sheet")
                        description = data.get("description")
                        volume = data.get("volume")
                        department = data.get("department")
                        unit = data.get("unit")
                        work_order_number = data.get("work_order_number")
                        pdr_number = data.get("pdr_number")
                        letter_number = data.get("letter_number")
                        approved_date = data.get("approved_date")
                        revision = data.get("revision")

                        instance = Drawing.objects.create(
                            drawing_type=drawing_type,
                            drawing_number=drawing_number,
                            supplier_name=supplier_name,
                            vendor_number=vendor_number,
                            client_number=client_number,
                            package_number=package_number,
                            drawing_size=drawing_size,
                            drawing_file_type=drawing_file_type,
                            is_layout=is_layout,
                            is_dwg_file_present=is_dwg_file_present,
                            date_of_registration=date_of_registration,
                            certification=certification,
                            no_of_sheet=no_of_sheet,
                            sub_volume=volume,
                            department=department,
                            unit=unit,
                            remarks=remarks,
                            revision_version = revision,
                            uploaded_by=request.user,
                            work_order_number=work_order_number,
                            letter_number=letter_number,
                            fdr_approved_date=approved_date,
                            pdr_number=pdr_number,
                        )
                        for desindex in range(no_of_sheet):
                            item = description[min(desindex, len(description) - 1)]
                            if desindex == 0:
                                instance.default_description = item
                                instance.save()
                            DrawingDescription.objects.create(
                                index=desindex + 1, drawing=instance, description=item
                            )

                        DrawingLog.objects.create(
                            user=request.user,
                            drawing=instance,
                            status="Add Drawing",
                            message="Drawing added from bulk upload",
                            details=f"add drawing data from bulk upload excel file",
                        )
                response = {
                    "success": True,
                    "message": "Drawings created successfully.",
                    "results": {
                        "error_data_set": error_data_set
                    },
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Failed to create drawings.",
                    "results": {
                        "error_data_set": error_data_set
                    },
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    # upload bulk drawing file
    @allowed_admin_user
    def put(self, request):
        try:
            data = request.data
            file_list = data.getlist("file_list", [])
            is_file_list_valid = all(
                isinstance(file, InMemoryUploadedFile) or isinstance(file, UploadedFile)
                for file in file_list
            )
            if not is_file_list_valid:
                response = {"success": False, "message": "Upload valid files."}
                return Response(response, status=400)

            error_drawing_list = []
            new_drawing_with_file_list = []

            for file in file_list:
                file_name, file_ext = get_file_name_and_extension(file.name)
                if file_ext not in ["PDF", "TIF", "TIFF", "DWG"]:
                    error_drawing_list.append(f"Invalid file extension {file.name}")
                    continue

                drawing_type, drawing_number = extract_drawing_type_number(file_name)

                if not drawing_type and not drawing_number:
                    error_drawing_list.append(f"Invalid file name {file.name}")
                    continue
                try:
                    drawing = Drawing.objects.get(
                        drawing_number=drawing_number, drawing_type=drawing_type
                    )
                    if drawing.is_archive:
                        error_drawing_list.append(f"Drawing was archived {file.name}")
                        continue
                    if drawing.is_approved:
                        error_drawing_list.append(f"Drawing was approved {file.name}")
                        continue
                except Drawing.DoesNotExist:
                    error_drawing_list.append(f"Drawing does not exist {file.name}")
                    continue

                if drawing.no_of_sheet > 1:
                    actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}SH{i}" for i in range(1, drawing.no_of_sheet + 1)]
                else:
                    actual_file_name_list = [f"{drawing.drawing_type}-{drawing.drawing_number}"]

                if file_name not in actual_file_name_list:
                    error_drawing_list.append(f"Invalid file name {file.name}")
                    continue
                if len(error_drawing_list) == 0:
                    new_drawing_with_file_list.append({"file":file,"drawing":drawing})

            # end validation file
            if new_drawing_with_file_list:
                same_name_dwg_files = []
                all_files = []
                for item in new_drawing_with_file_list:
                    file = item['file']
                    drawing = item['drawing']
                    file_name, extension = get_file_name_and_extension(file.name)
                      # Get the last extension (case-insensitive)
                    if drawing.is_dwg_file_present and extension == "DWG":
                        if exist_corresponding_tif_pdf(file_name, file_list):
                            same_name_dwg_files.append(file)
                    else:
                        all_files.append({"file":file,"drawing":drawing})

                with transaction.atomic():
                    for item in all_files:
                        file = item['file']
                        drawing = item['drawing']
                        dwg_file = None
                        file_name, file_ext = get_file_name_and_extension(file.name)

                        if drawing.is_dwg_file_present and file_ext != "DWG":
                            dwg_file = find_corresponding_dwg(file_name, same_name_dwg_files)

                        if not DrawingFile.objects.filter(drawing=drawing, file_name=file_name).exists():
                            # when create new drawing the core file not be .dwg file
                            DrawingFile.objects.create(drawing=drawing, file=file, dwg_file=dwg_file, file_name=file_name)

                            if drawing.no_of_sheet == drawing.files.count():
                                drawing.is_file_present = True
                                if request.user.is_superuser:
                                    drawing.is_approved = True
                                    drawing.approved_by = request.user
                            else:
                                drawing.is_file_present = False
                                drawing.approved_by = None
                                drawing.is_approved = False
                            drawing.save()

                            # create drawing log
                            DrawingLog.objects.create(
                                user=request.user,
                                drawing=drawing,
                                status="Add Drawing",
                                message="Drawing files added from bulk upload",
                                details=f"add new file. {file.name}",
                            )

                    response = {
                        "success": True,
                        "message": "Drawing file uploaded successfully.",
                        "results": error_drawing_list,
                    }
                    return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Failed to upload drawing file.",
                    "results": error_drawing_list,
                }
                return Response(response, status=400)

        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class DownalodDrawingFileApiView(APIView):
    def get(self, request, id):
        try:
            try:
                instance = DrawingFile.objects.get(id=id)
            except DrawingFile.DoesNotExist:
                response = {"success": False, "message": "Drawing file does not exist"}
                return Response(response, status=400)
            
            if request.user.role == "User":
                perms = request.user.drawing_permission
                if instance.drawing.is_layout and not validateDrawingPerm(perms, 'view_layout'):
                    return Response({
                    "success": False,
                    "message": "Required View Layout Permission.",
                    "results": None,
                    }, status=400)
                
                if not validateDrawingPerm(perms, instance.drawing.drawing_type.lower()):
                    return Response({
                        "success": False,
                        "message": "Required View  Permission.",
                        "results": None,
                    }, status=400)

            action = request.GET.get("action", "view")
            log_message = "drawing viewed"
            log_status = "View Drawing"

            if action == "download":
                dwg_download = request.GET.get("dwg_download", "no") == "yes"
                if dwg_download and  request.user.role == "User" and not request.user.drawing_permission.get('download_drawing', False):
                    return Response(
                        {
                            "success": False,
                            "message": "Required Download DWG Permission",
                        },
                        status=400,
                    )
                if dwg_download:
                    if instance.dwg_file:
                        file_path = instance.dwg_file.path
                        log_message = f"Drawing DWG file {instance.file_name} downloaded"
                    else:
                        raise ValueError("DWG File is not present")
                else:
                    file_path = instance.file.path
                    log_message = f"download drawing file {instance.file_name}"
                log_status = "Download Drawing"
            else:
                log_message = f"Drawing file {instance.file_name} viewed"
                log_status = "View Drawing"
                if instance.drawing.drawing_file_type == "TIF":
                    file_path = instance.view_pdf_file.path
                else:
                    file_path = instance.file.path

            if os.path.exists(file_path):
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=instance.drawing,
                    status=log_status,
                    message=log_message,
                    details=log_message,
                )
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return Response(
                    {"success": False, "message": "File not found."}, status=400
                )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DrawingDescriptionApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingDescriptionSerializer

    def get(self, request, drawing_id):
        try:
            # retrive single object of user model
            try:
                filter_criteria = Q(id=drawing_id)
                if request.user.role == "User":
                    filter_criteria &= Q(is_archive=False, is_approved=True)
                instance = Drawing.objects.get(filter_criteria)
                if request.user.role == "User":
                    perms = request.user.drawing_permission
                    if instance.is_layout and not validateDrawingPerm(perms, 'view_layout'):
                        return Response({
                        "success": False,
                        "message": "Required View Layout Permission.",
                        "results": None,
                        }, status=400)
                    if not validateDrawingPerm(perms, instance.drawing_type.lower()):
                        return Response({
                            "success": False,
                            "message": "Required View  Permission.",
                            "results": None,
                        }, status=400)
            except Drawing.DoesNotExist:
                response = {"success": False, "message": "Drawing does not exist"}
                return Response(response, status=400)
            # retrive list of user object according to filter_criteria

            filter_criteria = Q(drawing=drawing_id)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(description__icontains=query)
                    | Q(index__icontains=query)
                    | Q(drawing_file__file_name__icontains=query)
                )

            instance = (
                DrawingDescription.objects.select_related()
                .filter(filter_criteria)
                .order_by("index").distinct()
            )

            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(
                instance, many=True, context={"request": request}
            )
            return Response(serializer.data, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_admin_user
    def put(self, request, drawing_id):
        try:
            data = request.data
            description_id = data.get("id", None)
            description = data.get("description", None)

            if not all([description_id, description]):
                response = {"success": False, "message": "All the mandatory fields are required."}
                return Response(response, status=400)
            try:
                instance = DrawingDescription.objects.get(
                    id=description_id, drawing__id=drawing_id
                )
            except Drawing.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Drawing Descrption not found.",
                }
                return Response(response, status=400)

            with transaction.atomic():
                if instance.description != description:
                    log_details = f"Description-{instance.index}: {instance.description} ➡️ {description}"
                    instance.description = description
                    instance.save()
                    if instance.index == 1:
                        drawing = instance.drawing
                        drawing.default_description = description
                        drawing.save()
                    DrawingLog.objects.create(
                        user=request.user,
                        drawing=instance.drawing,
                        status="Update Drawing",
                        message="Drawing description updated",
                        details=log_details,
                    )

                response = {
                    "success": True,
                    "message": "Description updated successfully.",
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


class DrawingLogApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = DrawingLogListSerializer

    def get(self, request, drawing_id=None):
        try:
            # retrive single object of user model
            filter_criteria = Q()
            query = request.GET.get("query", "")
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            drawing_type = request.GET.get("drawing_type", None)
            if drawing_id:
                try:
                    if request.user.role == "User":
                        response = {
                            "success": True,
                            "message": "User can't not view drawing Log",
                            "results": [],
                            "count":0
                        }
                        return Response(response, status=400)

                    drawing = Drawing.objects.get(id=drawing_id)
                    if drawing.is_layout and (request.user.role == "User" and not request.user.is_view_layout):
                        response = {
                            "success": False,
                            "message": "Required View Layout Permission.",
                            "results": None,
                        }
                        return Response(response, status=400)
                    filter_criteria &= Q(drawing=drawing)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                        )
                except Drawing.DoesNotExist:
                    response = {"success": False, "message": "Drawing does not exist"}
                    return Response(response, status=400)
            else:
                # retrive list of user object according to filter_criteria
                if query:
                    filter_criteria &= Q(
                        Q(drawing__drawing_type__icontains=query)
                        | Q(drawing__drawing_number__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
            if status:
                filter_criteria &= Q(status__in=status.split(","))
            if drawing_type:
                filter_criteria &= Q(drawing__drawing_type__in=drawing_type.split(","))
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

            if user_id := request.GET.get("user", None):
                filter_criteria &= Q(user__id__in=user_id.split(","))
            instance = (
                DrawingLog.objects.select_related()
                .filter(filter_criteria).only('id', 'message', 'details')
                .order_by("-action_time").distinct()
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


class DownloadDrawingLogExcelApiView(APIView):
    serializer_class = DrawingLogExcelListSerializer
    @allowed_superadmin
    def get(self, request):
        try:
            # retrive single object of user model
            filter_criteria = Q()
            query = request.GET.get("query", "")
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            if query:
                filter_criteria &= Q(
                    Q(drawing__drawing_type__icontains=query)
                    | Q(drawing__drawing_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )
            if status and any(status == item[0] for item in DRAWING_LOG_STATUS_CHOICE):
                filter_criteria &= Q(status__in=status.split(","))

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

            if drawing_type := request.GET.get("drawing_type", None):
                filter_criteria &= Q(drawing__drawing_type__in=drawing_type.split(","))

            if user_id := request.GET.get("user", None):
                filter_criteria &= Q(user__id__in=user_id.split(","))

            instance = (
                DrawingLog.objects.select_related("user", "drawing")
                .filter(filter_criteria)
                .order_by("-action_time")
            )
            serializer = self.serializer_class(instance, many=True)
            return Response(
                {
                    "message": "MIS Report Downloaded",
                    "results": serializer.data,
                    "count": instance.count(),
                },
                status=200,
            )
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)



class DownlaodDrawingZipFile(APIView):
    @allowed_superadmin
    def get(self, request):
        try:
            MAX_ZIP_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB in bytes
            # retrive single object of user model
            filter_criteria = Q()
            query = request.GET.get("query", "")
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            if query:
                filter_criteria &= Q(
                    Q(drawing__drawing_type__icontains=query)
                    | Q(drawing__drawing_number__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )

            if status and any(status == item[0] for item in DRAWING_LOG_STATUS_CHOICE):
                filter_criteria &= Q(status__in=status.split(","))
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

            if drawing_type := request.GET.get("drawing_type", None):
                filter_criteria &= Q(drawing__drawing_type__in=drawing_type.split(","))

            if user_id := request.GET.get("user", None):
                filter_criteria &= Q(user__id__in=user_id.split(","))

            drawing_ids = DrawingLog.objects.select_related("user", "drawing").filter(filter_criteria).values_list("drawing__id")
            drawing_files = DrawingFile.objects.filter(drawing__id__in=drawing_ids)

            media_root = settings.MEDIA_ROOT  # Assuming media files are stored here

            # Calculate total size of files, checking for existence on the filesystem
            total_size = 0
            files_to_zip = []
            for df in drawing_files:
                if df.file and df.file.name:
                    file_path = os.path.join(media_root, df.file.name)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        files_to_zip.append((df.file.name, file_path))
                
                if df.dwg_file and df.dwg_file.name:
                    dwg_file_path = os.path.join(media_root, df.dwg_file.name)
                    if os.path.is_file(dwg_file_path):
                        dwg_file_size = os.path.getsize(dwg_file_path)
                        total_size += dwg_file_size
                        files_to_zip.append((df.dwg_file.name, dwg_file_path))

            if total_size == 0:
                return HttpResponse("drawing file not found.", status=400)
            
            elif total_size > MAX_ZIP_SIZE:
                return HttpResponse("The selected files exceed the 2 GB limit.", status=400)
            
            # Create an in-memory zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, file_path in files_to_zip:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        zip_file.writestr(file_name, file_content)
            
            # Set up the response
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=drawings_files_from_logs.zip'
            return response

        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchDrawingApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = SearchDrawingSerializer

    def get(self, request):
        try:
            filter_criteria = Q(is_archive=False)
            if query := request.GET.get("query"):
                drawing_type, drawing_number = extract_drawing_type_number(
                    query.upper()
                )
                if drawing_type:
                    if drawing_number:
                        filter_criteria &= Q(
                            Q(drawing_type=drawing_type),
                            Q(drawing_number__icontains=drawing_number),
                        )
                    else:
                        filter_criteria &= Q(drawing_type=drawing_type)
                else:
                    filter_criteria &= Q(
                        Q(drawing_type__icontains=query)
                        | Q(drawing_number__icontains=query)
                    )

            if request.user.role == "User":
                filter_criteria &= Q(is_archive=False, is_approved=True)
                if drawing_type and not validateDrawingPerm(request.user.drawing_permission, drawing_type.lower()):
                    return Response({
                        "success": False,
                        "message": "Required View  Permission.",
                        "results": None,
                    }, status=400)
            instance = Drawing.objects.filter(filter_criteria).values('id', 'drawing_type', 'drawing_number', 'drawing_number_numeric').order_by('drawing_number_numeric')
            # Paginate the results using the custom pagination class
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class BulkArchiveDrawingApiView(APIView):
    serializer_class = DrawingListSerializer
    pagination_class = CustomPagination


    @allowed_superadmin
    def get(self, request):
        try:
            # retrive list of user object according to filter_criteria
            filter_criteria = Q(is_archive=False)
            if drawing_type := request.GET.get("drawing_type"):
                filter_criteria &= Q(drawing_type=drawing_type)

            if work_order_number := request.GET.get("work_order_number"):
                filter_criteria &= Q(work_order_number__icontains=work_order_number)

            if description := request.GET.get("description"):
                filter_criteria &= Q(description__description__icontains=description)

            if department_id := request.GET.get("department_id"):
                filter_criteria &= Q(department__department_id=department_id)

            if unit_id := request.GET.get("unit_id"):
                filter_criteria &= Q(unit__unit_id=unit_id)

            if query := request.GET.get("query"):
                drawing_type, drawing_number = extract_drawing_type_number(
                    query.upper()
                )
                if drawing_type:
                    if drawing_number:
                        filter_criteria &= Q(
                            Q(drawing_type=drawing_type),
                            Q(drawing_number__icontains=drawing_number),
                        )
                    else:
                        filter_criteria &= Q(drawing_type=drawing_type)
                else:
                    filter_criteria &= Q(
                        Q(drawing_type__icontains=query)
                        | Q(drawing_file_type__icontains=query)
                        | Q(drawing_number__icontains=query)
                        | Q(department__name__icontains=query)
                        | Q(department__department_id__icontains=query)
                        | Q(unit__name__icontains=query)
                        | Q(unit__unit_id__icontains=query)
                        | Q(remarks__icontains=query)
                        | Q(description__description__icontains=query)
                    )
            instance = (
                Drawing.objects.select_related()
                .filter(filter_criteria)
                .order_by("-created_at").distinct()
            )
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(instance, request, view=self)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                result = paginator.get_paginated_response(serializer.data)
                return result

            serializer = self.serializer_class(instance, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            drawing_list = data.get("drawing_list", [])
            archive_reason = data.get("archive_reason", None)
            if not drawing_list:
                response = {"success": False, "message": "Required drawing list"}
                return Response(response, status=400)
            if not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)

            for drawing in Drawing.objects.filter(id__in=drawing_list, is_archive=False):
                DrawingLog.objects.create(
                    user=request.user,
                    drawing=drawing,
                    status="Archive Drawing",
                    message="Drawing archived",
                    details=f"archive reason : {archive_reason}",
                )
                drawing.is_archive=True
                drawing.archive_reason=archive_reason
                drawing.save()

            response = {
                "success": True,
                "message": "Drawings Archived successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }

