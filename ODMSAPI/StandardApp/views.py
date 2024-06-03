import json
from django.shortcuts import render
from django.db import transaction
from django.http import FileResponse
# Create your views here.
from .serializers import (
    StandardDetailSerializer,
    StandardSerializer,
    RSNVolumeSerializer,
    RSNGroupSerializer,
    IPSSTitleSerializer,
    SearchRsnGroupSerializer,
    SearchRsnVolumeSerializer,
    SearchIPSSTitleSerializer,
    StandardLogSerializer,
    StandardLogExcelSerializer,
    StandardArchiveSerializer,
    )
from .models import (
    Standard,
    RSNVolume,
    RSNGroup,
    IPSSTitle,
    StandardLog,
    STANDARD_LOG_STATUS_CHOICE
    )
from rest_framework.views import APIView
from rest_framework.response import Response
from AuthApp.pagination import CustomPagination
from AuthApp.models import Subvolume
from core.utility import Syserror, check_file, get_file_name
from django.db.models import Q, Count, Value, F
from django.db.models.functions import Concat
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
import os
from AuthApp.customAuth import allowed_superadmin, allowed_admin_user
from datetime import datetime




# RSN Volume APIView        
class RSNVolumeAPIView(APIView):
    pagination_class = CustomPagination
    serializer_class = RSNVolumeSerializer
    @allowed_admin_user
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    instance = RSNVolume.objects.get(filter_criteria)
                except RSNVolume.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Rsn Volume doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = RSNVolumeSerializer(instance)
                response = {
                    "success": True,
                    "message": "Rsn Volume data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q()
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(volume_no__icontains=query)
                        | Q(volume_title__icontains=query)
                    )
                instance = RSNVolume.objects.filter(filter_criteria).order_by("volume_no").distinct()
                
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)
                
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Rsn Volume data retrieved successfully.",
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
    def post(self, request):
        try:
            data = request.data
            volume_no = data.get("volume_no", None)
            volume_title = data.get("volume_title", None)
            
            if not all([volume_no, volume_title]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if RSNVolume.objects.filter(volume_no=volume_no).exists():
                response = {
                    "success": False,
                    "message": "Rsn Volume number already exist."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance = RSNVolume.objects.create(
                    volume_no = volume_no,
                    volume_title = volume_title
                )
                instance.save()
                response = {
                    "success": True,
                    "message": "Rsn Volume created successfully.",
                    "results": {
                        "id": instance.id,
                        "volume_no": instance.volume_no,
                        "volume_title": instance.volume_title
                    }
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
            id = data.get("id", None)
            volume_no = data.get("volume_no", None)
            volume_title = data.get("volume_title", None)
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = RSNVolume.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "RSN Volume not found"
                }
                return Response(response, status=400)

            if RSNVolume.objects.filter(volume_no=volume_no).exclude(volume_no=instance.volume_no).exists():
                response = {
                    "success": False,
                    "message": "Rsn Volume number already exist.",
                }
                return Response(response, status=400)
            
            
            with transaction.atomic():
                instance.volume_no = volume_no
                instance.volume_title = volume_title
                instance.save()
                response = {
                    "success": True,
                    "message": "Rsn Volume updated successfully.",
                    "results": {
                        "id": instance.id,
                        "volume_no": instance.volume_no,
                        "volume_title": instance.volume_title
                    }
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
          
# RSN Group APIView
class RSNGroupAPIView(APIView):
    pagination_class = CustomPagination
    serializer_class = RSNGroupSerializer
    
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    instance = RSNGroup.objects.get(filter_criteria)
                except RSNGroup.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "RSN Group doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = RSNGroupSerializer(instance)
                response = {
                    "success": True,
                    "message": "RSN Group data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q()
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(name__icontains=query)
                        | Q(group_id__icontains=query)
                        | Q(rsn_volume__volume_no__icontains=query)
                        | Q(rsn_volume__volume_title__icontains=query)
                    )
                instance = RSNGroup.objects.select_related("rsn_volume").filter(filter_criteria).order_by("name").distinct()
                
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)
                
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Rsn Group data retrieved successfully.",
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
    def post(self, request):
        try:
            data = request.data
            name = data.get("name", None)
            group_id = data.get("group_id", None)
            rsn_volume = data.get("rsn_volume", None)
            
            if not all([name,group_id]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if RSNGroup.objects.filter(name=name).exists():
                response = {
                    "success": False,
                    "message": "Rsn Group name already exist.",
                }
                return Response(response, status=400)
            
            if group_id:
                if RSNGroup.objects.filter(group_id=group_id).exists():
                    response = {
                        "success": False,
                        "message": "Rsn Group ID already exist.",
                    }
                    return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required Group ID."
                }
                return Response(response, status=400)
            
            if rsn_volume:
                    try:
                        rsn_volume = RSNVolume.objects.get(id=rsn_volume)
                    except RSNVolume.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Rsn Volume not found."
                        }
                        return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required RSN Volume"
                }
                return Response(response, status=400)
                
            
            with transaction.atomic():
                instance = RSNGroup.objects.create(
                    name=name,
                    group_id = group_id,
                    rsn_volume = rsn_volume
                )
                instance.save()
                response = {
                    "success": True,
                    "message": "Rsn Group created successfully.",
                    "results": {
                        "id": instance.id,
                        "group_id": instance.group_id,
                        "name": instance.name,
                        "rsn_volume": {
                            "id": instance.rsn_volume.id if rsn_volume else None,
                            "volume_no": instance.rsn_volume.volume_no if rsn_volume else None,
                            "volume_title": instance.rsn_volume.volume_title if rsn_volume else None,
                        }
                    }
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
            id = data.get("id", None)
            group_id = data.get("group_id", None)
            name = data.get("name", None)
            rsn_volume = data.get("rsn_volume", None)
            
            if not all([name,group_id]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            instance = RSNGroup.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "RSN Group not found."
                }
                return Response(response, status=400)
            
            if RSNGroup.objects.filter(name=name).exclude(name=instance.name).exists():
                response = {
                    "success": False,
                    "message": "Group name already exist.",
                }
                return Response(response, status=400)
            
            if group_id:
                if RSNGroup.objects.filter(group_id=group_id).exclude(group_id=instance.group_id).exists():
                    response = {
                        "success": False,
                        "message": "Rsn Group ID already exist.",
                    }
                    return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required Group ID."
                }
                return Response(response, status=400)
            
            if rsn_volume:
                    try:
                        rsn_volume = RSNVolume.objects.get(id=rsn_volume)
                    except RSNVolume.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Rsn Volume not found."
                        }
                        return Response(response, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Required RSN Volume"
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance.name=name
                instance.group_id = group_id
                instance.rsn_volume = rsn_volume
                instance.save()
                response = {
                    "success": True,
                    "message": "RSN Group updated successfully.",
                    "results": {
                        "id": instance.id,
                        "group_id": instance.group_id,
                        "name": instance.name,
                        "rsn_volume": {
                            "id": instance.rsn_volume.id if rsn_volume else None,
                            "volume_no": instance.rsn_volume.volume_no if rsn_volume else None,
                            "volume_title": instance.rsn_volume.volume_title if rsn_volume else None,
                        }
                    }
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)

# IPSS Title APIView
class IPSSAPIView(APIView):
    pagination_class = CustomPagination
    serializer_class = IPSSTitleSerializer
    
    @allowed_admin_user
    def get(self, request, id=None):
        try:
            if id:
                try:
                    filter_criteria = Q(id=id)
                    instance = IPSSTitle.objects.get(filter_criteria)
                except IPSSTitle.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "IPSS doesn't exist.",
                    }
                    return Response(response, status=400)
                serializer = IPSSTitleSerializer(instance)
                response = {
                    "success": True,
                    "message": "IPSS data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q()
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(title__icontains=query)
                        | Q(title_id__icontains=query)
                    )
                instance = IPSSTitle.objects.filter(filter_criteria).order_by("title_id").distinct()
                
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)
                
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                    
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "IPSS data retrieved successfully.",
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
    def post(self, request):
        try:
            data = request.data
            title = data.get("title", None)
            title_id = data.get("title_id", None)
            
            if not all([title, title_id]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            if IPSSTitle.objects.filter(title=title).exists():
                response = {
                    "success": False,
                    "message": "Title already exist"
                }
                return Response(response, status=400)
            
            if IPSSTitle.objects.filter(title_id=title_id).exists():
                response = {
                    "success": False,
                    "message": "Title ID already exist."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance = IPSSTitle.objects.create(title=title, title_id=title_id)
                instance.save()
                response ={
                    "success": True,
                    "message": "IPSS Title created succesfully.",
                    "results": {
                        "id": instance.id,
                        "title": instance.title
                    }
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
            id = data.get("id", None)
            title = data.get("title", None)
            title_id = data.get("title_id", None)
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = IPSSTitle.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "IPSS title not found."
                }
                return Response(response, status=400)
            
            if IPSSTitle.objects.filter(title=title).exclude(title=instance.title).exists():
                response = {
                    "success": False,
                    "message": "Title already exist"
                }
                return Response(response, status=400)
            
            if IPSSTitle.objects.filter(title_id=title_id).exclude(title_id=instance.title_id).exists():
                response = {
                    "success": False,
                    "message": "Title ID already exist."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance.title=title
                instance.title_id=title_id
                instance.save()
                response ={
                    "success": True,
                    "message": "IPSS Title created succesfully.",
                    "results": {
                        "id": instance.id,
                        "title": instance.title,
                        "title_id": instance.title_id
                    }
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
              
# Standard APiView
class StandardAPIView(APIView):
    pagination_class = CustomPagination
    serializer_class = StandardSerializer
    
    def get(self, request, id=None):
        try:
            if request.user.role == "User" and not request.user.is_view_standard:
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
                    
                    instance = Standard.objects.get(filter_criteria)
                except Standard.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Standard doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = StandardDetailSerializer(instance)
                response = {
                    "success": True,
                    "message": "Standard retrieved successfully.",
                    "result": serializer.data
                }
                return Response(response, status=200)
            else:
                standard_type = request.GET.get("standard_type", "BIS")
                if not standard_type:
                    standard_type = "BIS"
                filter_criteria = Q(standard_type=standard_type, is_archive=False)
                if request.user.role == "User":
                    filter_criteria &= Q(is_approved=True)
                    
                if standard_type == "RSN":
                    if rsn_volume := request.GET.get("rsn_volume"):
                        filter_criteria &= Q(rsn_volume__id = rsn_volume)
                        
                    if group := request.GET.get("group"):
                        filter_criteria &= Q(group__id = group)
                        
                if query := request.GET.get("query"):
                    if standard_type == "BIS":
                        filter_criteria &= Q(
                        Q(standard_type__icontains=query)
                        | Q(standard_no__icontains=query)
                        | Q(description__icontains=query)
                        | Q(part_no__icontains=query)
                        | Q(section_no__icontains=query)
                        | Q(document_year__icontains=query)
                        | Q(division__icontains=query)
                        | Q(division_code__icontains=query)
                        | Q(committee_code__icontains=query)
                        | Q(committee_title__icontains=query)
                        )
                    elif standard_type == "RSN":
                        filter_criteria &= Q(
                        Q(standard_type__icontains=query)
                        | Q(standard_no__icontains=query)
                        | Q(rsn_volume__volume_title__icontains=query)
                        | Q(rsn_volume__volume_no__icontains=query)
                        | Q(group__name__icontains=query)
                        | Q(description__icontains=query)
                        | Q(no_of_sheet__icontains=query)
                        )
                    elif standard_type == "IPSS":
                        filter_criteria &= Q(
                        Q(standard_type__icontains=query)
                        | Q(standard_no__icontains=query)
                        | Q(description__icontains=query)
                        | Q(title__title__icontains=query)
                        | Q(title__title_id__icontains=query)
                        | Q(file_availability__icontains=query)
                        )
                    else:
                        filter_criteria &= Q(
                        Q(standard_type__icontains=query)
                        | Q(standard_no__icontains=query)
                        | Q(description__icontains=query)
                        | Q(part_no__icontains=query)
                        | Q(section_no__icontains=query)
                        | Q(document_year__icontains=query)
                        )
                instance = Standard.objects.select_related('rsn_volume').filter(filter_criteria).order_by("standard_no_numeric")

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
                    "message": "Standards retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success":False, "message":str(e)}
            return Response(response, status=400)
    
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            standard_type = data.get("standard_type", None) or None
            standard_number = data.get("standard_number", None) or None
            part_no = data.get("part_number", None) or None
            section_no = data.get("section_number", None) or None
            document_year = data.get("document_year", None) or None
            division = data.get("division", None) or None 
            division_code = data.get("division_code", None) or None
            committee_code = data.get("committee_code", None) or None
            committee_title = data.get("committee_title", None) or None
            description = data.get("description", None) or None
            rsn_volume = data.get("rsn_volume", None) or None
            group = data.get("group", None) or None
            no_of_sheet = data.get("no_of_sheet", None) or None
            title = data.get("title", None) or None
            file = data.get("file", None) or None
            file_availability = data.get("file_availability", "NO") == "YES"
            
            if not all([standard_number, standard_type]):
                response = {
                    "success": False,
                    "message": "Required all fields!",
                }
                return Response(response, status=400)
            if standard_type == "BIS":
                rsn_volume = None
                group = None
                no_of_sheet = None
                title = None
                file_availability = None
            elif standard_type in ["ASTM","AWWA","BRITISH","DIN(GERMAN)","GOST(RUSSIAN)","IEC","ISO","IRST","API","PSN_approved"]:
                division = None
                division_code = None
                committee_code = None
                committee_title = None
                rsn_volume = None
                group = None
                no_of_sheet = None
                title = None
                file_availability = None
            elif standard_type == "RSN":
                part_no = None
                section_no = None
                document_year = None
                title = None
                committee_code = None
                committee_title = None
                file_availability = None
                
                if no_of_sheet:
                    if not no_of_sheet.isdigit() or int(no_of_sheet) < 1:
                        response ={
                            "success": False,
                            "message": "Invalid number of sheet"
                        }
                        return Response(response, status=400)
                else:
                    no_of_sheet = None
                
                if rsn_volume:
                    try:
                        rsn_volume = RSNVolume.objects.get(id=rsn_volume)
                    except RSNVolume.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Volume doesn't exist."
                        }
                        return Response(response, status=400)
                else:
                    rsn_volume = None
                
                if group:
                    try:
                        group = RSNGroup.objects.get(id=group, rsn_volume=rsn_volume)
                    except RSNGroup.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Group doesn,t exist"
                        }
                        return Response(response, status=400)
                else:
                    group = None 
                    rsn_volume = None
                
            elif standard_type == "IPSS":
                division = None
                division_code = None
                committee_code = None
                committee_title = None
                rsn_volume = None
                group = None
                no_of_sheet = None
                part_no = None
                section_no = None
                document_year = None
                
                if file_availability:
                    if not file:
                        response = {
                            "success": False,
                            "message": "Required file"
                        }
                        return Response(response, status=400)
                else:
                    file = None
                    
                if title:
                    try:
                        title = IPSSTitle.objects.get(id=title)
                    except IPSSTitle.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Title doesn't exist"
                        }
                        return Response(response, status=400)
                else:
                    title = None
            else:
                response = {
                    "success":False,
                    "message":"Invalid standard type"
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
                        "message": "Upload a PDF file."
                    }
                    return Response(response, status=400)
            else:
                file = None
                
            with transaction.atomic():
                instance = Standard.objects.create(
                    standard_type = standard_type,
                    standard_no = standard_number,
                    part_no = part_no,
                    section_no = section_no,
                    document_year = document_year,
                    division = division,
                    division_code = division_code,
                    committee_code = committee_code,
                    committee_title = committee_title,
                    description = description,
                    rsn_volume = rsn_volume,
                    group = group,
                    upload_file = file,
                    no_of_sheet = no_of_sheet,
                    title = title,
                    file_availability = file_availability,
                    is_approved = request.user.is_superuser
                )
                instance.save()
                # log create
                StandardLog.objects.create(
                    user = request.user,
                    standard = instance,
                    status = "Add Standard",
                    message = "Standard added",
                    details = f'Standard data added',
                )
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Standard created successfully.",
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
            id = data.get("id", None)
            part_no = data.get("part_number", None) or None
            section_no = data.get("section_number", None) or None
            document_year = data.get("document_year", None) or None
            division = data.get("division", None) or None
            division_code = data.get("division_code", None) or None
            committee_code = data.get("committee_code", None) or None
            committee_title = data.get("committee_title", None) or None
            description = data.get("description", None) or None
            rsn_volume = data.get("rsn_volume", None) or None
            group = data.get("group", None) or None
            no_of_sheet = data.get("no_of_sheet", None) or None
            title = data.get("title", None) or None
            file_availability = data.get("file_availability", "NO") == "YES"
            file = data.get("file", None) or None

            if not id:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
            
            instance = Standard.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Standard Not Found"
                }
                return Response(response, status=400)
            if instance.standard_type == "BIS":
                rsn_volume = None
                group = None
                no_of_sheet = None
                title = None
                file_availability = None
                file_path = None
                
            elif instance.standard_type in ["ASTM","AWWA","BRITISH","DIN(GERMAN)","GOST(RUSSIAN)","IEC","ISO","IRST","API","PSN_approved"]:
                division = None
                division_code = None
                committee_code = None
                committee_title = None
                rsn_volume = None
                group = None
                no_of_sheet = None
                title = None
                file_availability = None
                file_path = None
                
            elif instance.standard_type == "RSN":
                part_no = None
                section_no = None
                document_year = None
                committee_code = None
                committee_title = None
                title = None
                file_availability = None
                file_path = None
                
                if no_of_sheet:
                    if not no_of_sheet.isdigit() or int(no_of_sheet) < 1:
                        response = {
                            "success": False,
                            "message": "Invalid number of sheet!"
                        }
                        return Response(response, status=400)
                else:
                    no_of_sheet = None
                    
                if rsn_volume:
                    try:
                        rsn_volume = RSNVolume.objects.get(id=rsn_volume)
                    except RSNVolume.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Rsn Volume doesn't exist."
                        }
                        return Response(response, status=400)
                else:
                    rsn_volume = None
                
                if group:
                    try:
                        group = RSNGroup.objects.get(id=group, rsn_volume=rsn_volume)
                    except RSNGroup.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Rsn Group doesn't exist."
                        }
                        return Response(response, status=400)
                else:
                    group = None
                    rsn_volume = None
                    
            elif instance.standard_type == "IPSS":
                division = None
                division_code = None
                committee_code = None
                committee_title = None
                rsn_volume = None
                group = None
                no_of_sheet = None
                part_no = None
                section_no = None
                document_year = None
                file_path = None
                if file and file_availability:
                    if instance.upload_file:
                        file_path = instance.upload_file.path  # to delete old file  
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
                            "message": "Upload a PDF file."
                        }
                        return Response(response, status=400)
                    
                elif not instance.upload_file and not file and file_availability:
                    response = {
                            "success": False,
                            "message": "Required file."
                        }
                    return Response(response, status=400)
                
                elif instance.upload_file and not file_availability:
                    file_path = instance.upload_file.path # to delete old file 
                    file = None
                else:
                    file = None
                
                if title:
                    try:
                        title = IPSSTitle.objects.get(id=title)
                    except IPSSTitle.DoesNotExist:
                        response = {
                            "success": False,
                            "message": "Title doesn't exist"
                        }
                        return Response(response, status=400)
                else:
                    title = None
            else:
                response = {
                    "success":False,
                    "message":"Invalid standard type"
                }
                return Response(response, status=400)
            
            log_details = ""
            with transaction.atomic():
                if instance.part_no != part_no:
                    log_details += f'Part No.: {instance.part_no} ➡️ {part_no} |'
                    instance.part_no = part_no
                    
                if instance.section_no != section_no:
                    log_details += f"Section No.:{instance.section_no} ➡️ {section_no} |"
                    instance.section_no = section_no
                    
                if instance.document_year != document_year:
                    log_details += f"Document Year : {instance.document_year} ➡️ {document_year} |"
                    instance.document_year = document_year
                    
                if instance.division != division:
                    log_details += f"Division : {instance.division} ➡️ {division} |"
                    instance.division = division
                    
                if instance.division_code != division_code:
                    log_details += f"Division Code : {instance.division_code} ➡️ {division_code} |"
                    instance.division_code = division_code
                    
                if instance.committee_code != committee_code:
                    log_details += f"Committee Code : {instance.committee_code} ➡️ {committee_code} |"
                    instance.committee_code = committee_code
                    
                if instance.committee_title != committee_title:
                    log_details += f"Committee Title : {instance.committee_title} ➡️ {committee_title} |"
                    instance.committee_title = committee_title
                    
                if instance.description != description:
                    log_details += f"Description : {instance.description} ➡️ {description} |"
                    instance.description = description
                    
                if instance.rsn_volume != rsn_volume:
                    log_details += f"Volume : {instance.rsn_volume.volume_title if instance.rsn_volume else None} ➡️ {rsn_volume.volume_title if rsn_volume else None} |"
                    instance.rsn_volume = rsn_volume
                    
                if instance.group != group:
                    log_details += f"Group : {instance.group.name if instance.group else None} ➡️ {group.name if group else None} |"
                    instance.group = group
                    
                if instance.no_of_sheet != no_of_sheet:
                    log_details += f"Number of Sheet : {instance.no_of_sheet} ➡️ {no_of_sheet} |"
                    instance.no_of_sheet = no_of_sheet
                    
                if instance.title != title:
                    log_details += f"Title : {instance.title.title if instance.title else None} ➡️ {title.title if title else None} |"
                    instance.title = title
                    
                if instance.file_availability != file_availability:
                    log_details += f"File Availability : {instance.file_availability} ➡️ {file_availability} |"
                    instance.file_availability = file_availability
                
                if instance.standard_type != "IPSS":
                    if file:
                        log_details += f"Upload File : {get_file_name(instance.upload_file.name)} ➡️ {file.name} |"
                        instance.is_approved = True if (not instance.is_approved and request.user.is_superuser) else False
                        instance.upload_file = file
                else:
                    if file and file_availability:
                        log_details += f"Upload File : {get_file_name(instance.upload_file.name)} ➡️ {file.name} |"
                        instance.is_approved = True if (not instance.is_approved and request.user.is_superuser) else False
                        instance.upload_file = file
                    
                    if instance.upload_file and not file_availability:
                        log_details += f"Upload File : {get_file_name(instance.upload_file.name)} ➡️ None |"
                        instance.is_approved = True if (not instance.is_approved and request.user.is_superuser) else False
                        instance.upload_file = None
                instance.save()
                
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)        #  deleting old file
                        
                if log_details:
                    StandardLog.objects.create(     # create log for update
                        user=request.user,
                        standard=instance,
                        status="Update Standard",
                        message="Standard updated",
                        details=log_details
                    )
                serializer = StandardDetailSerializer(instance)
                response = {
                    "success": True,
                    "message": "Standard updated successfully.",
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

# view standard file
class DownloadStandardFileApiView(APIView):
    def get(self, request, id):
        try:
            if request.user.role == "User" and not request.user.is_view_standard:
                response = {
                    "success": False,
                    "message": "Required permission to view."
                }
                return Response(response, status=400)
            try:
                instance = Standard.objects.get(id=id)
            except Standard.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Standard doesn't exist."
                }
                return Response(response, status=400)
            if instance.upload_file:
                file_path = instance.upload_file.path
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, "rb"))
                    StandardLog.objects.create(
                        user = request.user,
                        standard = instance,
                        status = "View Standard",
                        message = "View Standard File",
                        details = f'Standard File {get_file_name(file_path)} viewed.'
                    )
                    return response
                else:
                    return Response({"success":False, "message": "File not found."}, status=400)
            else:
                response = {
                    "success": False,
                    "message": "Standard file doesn't exist."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)       

# search Group
class SearchRsnGroupApiView(APIView):
    serializer_class = SearchRsnGroupSerializer
    
    def get(self, request, vol_id):
        try:
            filter_criteria = Q(rsn_volume__id=vol_id)
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(name_icontains=query) | Q(id_icontains=query)
                )
            
            instance = RSNGroup.objects.filter(filter_criteria).order_by("name").distinct()
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "RSN Group search list.",
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

# search Volume
class SearchRsnVolumeApiView(APIView):
    serializer_class = SearchRsnVolumeSerializer
    
    def get(self, request):
        try:
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(volume_title_icontains=query) | Q(id_icontains=query)
                )
            instance = RSNVolume.objects.filter(filter_criteria).order_by("volume_no").distinct()
            serializer = SearchRsnVolumeSerializer(instance, many=True)
            response = {
                "success": False,
                "message": "RSN Volume search list.",
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
        
# search IPSS
class SearchIPSSTitleApiView(APIView):
    serializer_class = SearchIPSSTitleSerializer
    def get(self, request):
        try:
            filter_criteria = Q()
            if query:= request.GET.get("query"):
                filter_criteria & Q(
                    Q(title_icontains=query) | Q(id_icontains=query)
                )
            instance = IPSSTitle.objects.filter(filter_criteria).order_by("title").distinct()
            serializer = SearchIPSSTitleSerializer(instance, many=True)
            response = {
                "success": True,
                "message": "IPSS Title search list",
                "results": serializer.data
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "Success": False,
                "message": str(e)
            }
            return Response(response, status=400)
        
# approve
class ApproveStandardApiView(APIView):
    
    @allowed_superadmin
    def get(self,request):
        standard_type = request.GET.get("standard_type", "BIS")
        instance = (Standard.objects.select_related().filter(
            is_archive=False, is_approved=False, standard_type =standard_type
        )).order_by("-created_at").distinct()
        serializer = StandardDetailSerializer(instance, many=True)
        response = {
            "success": True,
            "message": "Pending standard",
            "results": serializer.data
        }
        return Response(response, status=200)
    
    # approve single standard
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            standard_id = data.get("id", None)
            if not standard_id:
                response = {
                    "success": False,
                    "message": "Required standard ID."
                }
                return Response(response, status=400)
            try:
                standard = Standard.objects.get(id=standard_id, is_approved=False)
            except Standard.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Standard doesn't exist."
                }
                return Response(response, status=400)
            
            standard.is_approved = True
            standard.save()
            response = {
                "success": True,
                "message": "Standard approved successfully."
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
            standard_id_list = data.get("standard_id_list", [])
            if not standard_id_list:
                response = {
                    "success": False,
                    "message": "Required atleast one standard ID."
                }
                return Response(response, status=400)
            
            Standard.objects.filter(id__in=standard_id_list, is_archive=False, is_approved=False).update(is_approved=True)
            response = {
                "success": True,
                "message": "Standard approved successfully."
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
class ArchiveStandardApiView(APIView):
    serializer_class = StandardArchiveSerializer
     
    @allowed_superadmin
    def get(self, request):
        try:
            standard_type = request.GET.get("standard_type", "BIS")
            filter_criteria = Q(standard_type=standard_type, is_archive = True)
            if query := request.GET.get("query"):
                if standard_type == "BIS":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(description__icontains=query)
                    | Q(part_no__icontains=query)
                    | Q(section_no__icontains=query)
                    | Q(document_year__icontains=query)
                    | Q(division__icontains=query)
                    | Q(division_code__icontains=query)
                    | Q(committee_code__icontains=query)
                    | Q(committee_title__icontains=query)
                    )
                elif standard_type == "RSN":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(rsn_volume__volume_no__icontains=query)
                    | Q(rsn_volume__volume_title__icontains=query)
                    | Q(group__name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(no_of_sheet__icontains=query)
                    )
                elif standard_type == "IPSS":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(title__title__icontains=query)
                    | Q(description__icontains=query)
                    | Q(file_availability__icontains=query)
                    )
                else:
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(description__icontains=query)
                    | Q(part_no__icontains=query)
                    | Q(section_no__icontains=query)
                    | Q(document_year__icontains=query)
                    )
            instance = Standard.objects.select_related('rsn_volume').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Standards retrieved successfully.",
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
    
    #archive single standard
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            standard_id = data.get("id", None)
            is_archive = data.get("archive", False)
            archive_reason = data.get("archive_reason", None)
            if is_archive and not archive_reason:
                response = {"success": False, "message": "Required archive reason"}
                return Response(response, status=400)
            if not standard_id:
                response = {"success": False, "message": "Required standard ID"}
                return Response(response, status=400)
            try:
                standard = Standard.objects.get(id=standard_id)
            except Standard.DoesNotExist:
                response = {
                    "success": False,
                    "message": "Standard doesn't exist."
                }
                return Response(response, status=400)
            
            if is_archive:
                StandardLog.objects.create(
                    user = request.user,
                    standard = standard,
                    status = "Archive Standard",
                    message = "Standard archived",
                    details = f"Archive reason : {archive_reason}."
                )
            else:
                archive_reason = None
                StandardLog.objects.create(
                    user = request.user,
                    standard = standard,
                    status = "Update Standard",
                    message = "Standard unarchived",
                    details = f"Archive reason : {standard.archive_reason} ➡️ None."
                )
            standard.is_archive = is_archive
            standard.archive_reason = archive_reason
            standard.save()
            response = {
                "success": True,
                "message": f'Standard {"archived" if is_archive else "unarchived"} successfully.',
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
    
    # unarchive list of standard
    @allowed_superadmin
    def put(self, request):
        try:
            data = request.data
            standard_id_list = data.get("standard_id_list", [])
            if not standard_id_list:
                response = {"success": False, "message": "Required standard list"}
                return Response(response, status=400)
            for standard in Standard.objects.filter(id__in=standard_id_list, is_archive=True):
                StandardLog.objects.create(
                    user = request.user,
                    standard = standard,
                    status = "Update Standard",
                    message = "Standard unarchived",
                    details = f"Archive reason : {standard.archive_reason} ➡️ None."
                )
                standard.is_archive=False
                standard.archive_reason=None
                standard.save()
            response = {
                "success": True,
                "message": "Standard removed from archive successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
 
# delete
class StandardPermanentDeleteApiView(APIView):
    
    @allowed_superadmin
    def post(self, request):
        try:
            data = request.data
            standard_id_list = data.get("standard_id_list", [])
            if not standard_id_list:
                response = {"success": False, "message": "Required standard list"}
                return Response(response, status=400)
            
            standards = Standard.objects.filter(id__in=standard_id_list, is_archive=True)
            if not standards:
                response = {
                    "success": False,
                    "message": "No Standards found."
                }
                return Response(response, status=400)
            for i in standards:
                i.standardlog_set.annotate(
                        new_message=Concat(F("message"),Value(f" ({i.standard_type}-{i.standard_no} DELETED)"),)
                    ).update(message=F("new_message"))
                StandardLog.objects.create(
                    user = request.user,
                    standard =  None,
                    status = "Delete Standard",
                    message = f"{i.standard_type} deleted.",
                    details = f"Standard {i.standard_type}-{i.standard_no} DELETED.",
                )
                # attachment deletion will handle by model signal
                i.delete()
            response = {
                "success": True,
                "message": "Standards deleted successfully."
            }
            return Response(response, status=200)
                      
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

# log
class StandardLogApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = StandardLogSerializer
    
    def get(self, request, standard_id=None):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            standard_list = request.GET.get("standard", None)
            standard_type = request.GET.get("standard_type", None)
            if standard_id:
                try:
                    if request.user.role == "User":
                        standard = Standard.objects.get(id=standard_id, is_archive=False, is_approved=True)
                        filter_criteria &= Q(user=request.user)
                    else:
                        standard = Standard.objects.get(id=standard_id)
                    filter_criteria &= Q(standard=standard)
                    if query:
                        filter_criteria &= Q(
                            Q(user__full_name__icontains=query)
                            | Q(user__personnel_number__icontains=query)
                            | Q(message__icontains=query)
                        )  
                except Standard.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Standard doesn't exist."
                    }
                    return Response(response, status=400)
            else:
                if query:
                    filter_criteria &= Q(
                        Q(standard__standard_type__icontains=query)
                        | Q(standard__standard_no__icontains=query)
                        | Q(user__full_name__icontains=query)
                        | Q(user__personnel_number__icontains=query)
                        | Q(message__icontains=query)
                    )
                    
            if status:
                filter_criteria &= Q(status__in=status.split(','))
            
            if standard_type:
                filter_criteria &= Q(standard__standard_type__in=standard_type.split(','))
                
            if standard_list:
                filter_criteria &= Q(standard__id__in=standard_list.split(','))
                
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
            
            if user_id:
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                StandardLog.objects.select_related("user").filter(filter_criteria).order_by("-action_time").distinct()
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
class DownloadStandardLogExcelApiView(APIView):
    serializer_class = StandardLogExcelSerializer
    
    def get(self, request):
        try:
            filter_criteria = Q()
            query = request.GET.get("query", '')
            status = request.GET.get("status", None)
            user_id = request.GET.get("user", None)
            standard_list = request.GET.get("standard", None)
            if query:
                filter_criteria &= Q(
                    Q(standard__standard_type__icontains=query)
                    | Q(standard__standard_no__icontains=query)
                    | Q(user__full_name__icontains=query)
                    | Q(user__personnel_number__icontains=query)
                    | Q(message__icontains=query)
                )
                
            if status:
                filter_criteria &= Q(status__in=status.split(','))
                
            if standard_list:
                filter_criteria &= Q(standard__id__in=standard_list.split(','))
                
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
            
            if user_id:
                filter_criteria &= Q(user__id__in=user_id.split(','))
            instance = (
                StandardLog.objects.select_related().filter(filter_criteria).order_by("-action_time").distinct()
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
class BulkArchiveStandardApiView(APIView):
    serializer_class = StandardSerializer
    
    @allowed_superadmin
    def get(self, request):
        try:
            standard_type = request.GET.get("standard_type", "BIS")
            filter_criteria = Q(standard_type=standard_type, is_archive = False)
            if query := request.GET.get("query"):
                if standard_type == "BIS":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(description__icontains=query)
                    | Q(part_no__icontains=query)
                    | Q(section_no__icontains=query)
                    | Q(document_year__icontains=query)
                    | Q(division__icontains=query)
                    | Q(division_code__icontains=query)
                    | Q(committee_code__icontains=query)
                    | Q(committee_title__icontains=query)
                    )
                elif standard_type == "RSN":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(rsn_volume__volume_title__icontains=query)
                    | Q(group__name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(no_of_sheet__icontains=query)
                    )
                elif standard_type == "IPSS":
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(description__icontains=query)
                    | Q(file_availability__icontains=query)
                    )
                else:
                    filter_criteria &= Q(
                    Q(standard_type__icontains=query)
                    | Q(standard_no__icontains=query)
                    | Q(description__icontains=query)
                    | Q(part_no__icontains=query)
                    | Q(section_no__icontains=query)
                    | Q(document_year__icontains=query)
                    )
            instance = Standard.objects.select_related('rsn_volume').filter(filter_criteria).order_by("-created_at").distinct()
            
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Retrieve bulk archive Standards successfully.",
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
            standard_id_list = data.get("standard_id_list", [])
            archive_reason = data.get("archive_reason", None)
            if not standard_id_list:
                response = {"success": False, "message": "Required standard list."}
                return Response(response, status=400)
            
            if not archive_reason:
                response = {"success": False, "message": "Required archive reason."}
                return Response(response, status=400)
            
            for standard in Standard.objects.filter(id__in=standard_id_list, is_archive=False):
                standard.is_archive=True
                standard.archive_reason=archive_reason
                standard.save()
                StandardLog.objects.create(
                    user = request.user,
                    standard = standard,
                    status = "Archive Standard",
                    message = "Standard archived from bulk archive.",
                    details = f"Archive reason : {archive_reason}."
                )
            response = {
                "success": True,
                "message": "Standard archived successfully.",
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


# bulk upload   
class BulkUploadStandardApiView(APIView):
    serializer_class = StandardSerializer
    
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
                raise ValueError("invalid format of data list")
            
            new_data_list = []
            error_data_set = []
            for index, data in enumerate(data_list, start=2):
                standard_type = data.get("standard_type", "BIS")
                standard_no = data.get("standard_number", None) or None
                part_no = data.get("part_number", None) or None
                section_no = data.get("section_number", None) or None
                document_year = data.get("document_year", None) or None
                division = data.get("division", None) or None
                division_code = data.get("division_code", None) or None
                committee_code = data.get("committee_code", None) or None
                committee_title = data.get("committee_title", None) or None
                description = data.get("description", None) or None
                group = data.get("group_id", None) or None
                no_of_sheet = data.get("no_of_sheet", None) or None
                title_id = data.get("title_id", None) or None
                file_availability = data.get("file_availability", "NO") == "YES"
                file = data.get("file", None) or None
                    
                required_field = [
                    standard_type,
                    standard_no,
                ]

                if not all(required_field):
                    error_data_set.append(
                        {"row": index, "message": "Required mandatory fields."}
                    )
                    continue
                
                if standard_type == "BIS":
                    group = None
                    no_of_sheet = None
                    title_id = None
                    file_availability = None
                elif standard_type in ["ASTM","AWWA","BRITISH","DIN(GERMAN)","GOST(RUSSIAN)","IEC","ISO","IRST","API","PSN"]:
                    division = None
                    division_code = None
                    committee_code = None
                    committee_title = None
                    group = None
                    no_of_sheet = None
                    title_id = None
                    file_availability = None
                elif standard_type == "RSN":
                    part_no = None
                    section_no = None
                    document_year = None
                    title_id = None
                    committee_code = None
                    committee_title = None
                    file_availability = None
                    if not no_of_sheet or not str(no_of_sheet).isdigit() or int(no_of_sheet) < 1:
                        error_data_set.append(
                            {"row": index, "message": "Invalid number of sheet."}
                        )
                        continue
  
                    if group:
                            if group_exist := RSNGroup.objects.filter(group_id__icontains = group):
                                group = group_exist.first()
                            else:
                                error_data_set.append(
                                    {"row": index, "message": "Group doesn't exist."}
                                )
                                continue
                    else:
                        group = None 

                elif standard_type == "IPSS":
                    division = None
                    division_code = None
                    committee_code = None
                    committee_title = None
                    group = None
                    no_of_sheet = None
                    part_no = None
                    section_no = None
                    document_year = None
                    if title_id:
                        if title_exist := IPSSTitle.objects.filter(title_id__icontains = title_id):
                            title_id = title_exist.first()
                        else:
                            error_data_set.append(
                                {"row": index, "message": "Title doesn't exist."}
                            )
                            continue
                    else:
                        title_id = None
                else:
                    error_data_set.append(
                        {"row": index, "message": "Invalid standard type."}
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
                
                if standard_type == "IPSS" and not file_availability:
                    file = None
                elif standard_type == "IPSS" and file_availability and not file:
                    error_data_set.append({"row": index, "message": "Required file ."})
                    continue
                else:
                    if file:
                        if newfile := check_file(file_list, file):
                            file = newfile
                        else:
                            error_data_set.append(
                                {"row": index, "message": "File didn't match."}
                            )
                            continue
                
                if not error_data_set:
                    new_data_list.append({
                        "standard_no": standard_no,
                        "standard_type": standard_type,
                        "part_no": part_no,
                        "section_no": section_no,
                        "document_year": document_year,
                        "division": division,
                        "division_code": division_code,
                        "committee_code": committee_code,
                        "committee_title": committee_title,
                        "description": description,
                        "group": group,
                        "no_of_sheet": no_of_sheet,
                        "title_id": title_id,
                        "file_availability": file_availability,
                        "file": file
                    })
            if not error_data_set:
                with transaction.atomic():
                    for data in new_data_list:
                        standard_no = data.get("standard_no")
                        standard_type = data.get("standard_type")
                        part_no = data.get("part_no")
                        section_no = data.get("section_no")
                        document_year = data.get("document_year")
                        division = data.get("division")
                        division_code = data.get("division_code")
                        committee_code = data.get("committee_code")
                        committee_title = data.get("committee_title")
                        description = data.get("description")
                        group = data.get("group")
                        no_of_sheet = data.get("no_of_sheet")
                        title_id = data.get("title_id")
                        file_availability = data.get("file_availability")
                        file = data.get("file")
                        if group:
                            volume = group.rsn_volume
                        else:
                            volume = None
                                                    
                        instance = Standard.objects.create(
                            standard_type = standard_type,
                            standard_no = standard_no,
                            part_no = part_no,
                            section_no = section_no,
                            document_year = document_year,
                            division = division,
                            division_code = division_code,
                            committee_code = committee_code,
                            committee_title = committee_title,
                            description = description,
                            group = group,
                            rsn_volume = volume,
                            no_of_sheet = no_of_sheet,
                            title = title_id,
                            file_availability = file_availability if standard_type == "IPSS" else None,
                            upload_file = file,
                            is_approved = request.user.is_superuser
                        )
                        StandardLog.objects.create(
                            user = request.user,
                            standard = instance,
                            status = "Add Standard",
                            message = "Standard added from bulk upload.",
                            details = f"Add standard data from bulk upload excel file."
                        )
                response = {
                    "success": True,
                    "message": "Standard created successfully.",
                    "results": {
                        "error_data_set": error_data_set,
                    }
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Failed to create standards.",
                    "results": {
                        "error_data_set": error_data_set,
                    },
                }
                return Response(response, status=400)
                          
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)


class StandardCountApiView(APIView):
    @allowed_admin_user
    def get(self,request):
        status_type = request.GET.get("status_type", "Approved")
        try:
            if status_type == "Approved":
                standard = Standard.objects.select_related().aggregate(
                    bis_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="BIS")),
                    astm_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="ASTM")),
                    awwa_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="AWWA")),
                    british_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="BRITISH")),
                    din_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="DIN(GERMAN)")),
                    gost_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="GOST(RUSSIAN)")),
                    iec_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="IEC")),
                    iso_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="ISO")),
                    irst_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="IRST")),
                    api_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="API")),
                    psn_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="PSN")),
                    rsn_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="RSN")),
                    ipss_approved=Count("id", filter=Q(is_approved=True, is_archive=False, standard_type="IPSS")),
                    )
                data = {
                    "bis": standard["bis_approved"] or 0,
                    "astm": standard["astm_approved"] or 0,
                    "awwa": standard["awwa_approved"] or 0,
                    "british": standard["british_approved"] or 0,
                    "din": standard["din_approved"] or 0,
                    "gost": standard["gost_approved"] or 0,
                    "iec": standard["iec_approved"] or 0,
                    "iso": standard["iso_approved"] or 0,
                    "irst": standard["irst_approved"] or 0,
                    "api": standard["api_approved"] or 0,
                    "psn": standard["psn_approved"] or 0,
                    "rsn": standard["rsn_approved"] or 0,
                    "ipss": standard["ipss_approved"] or 0,
                }
            elif status_type == "Archived":      
                standard = Standard.objects.select_related().aggregate(
                    bis_archived=Count("id", filter=Q(is_archive=True, standard_type="BIS")),
                    astm_archived=Count("id", filter=Q(is_archive=True, standard_type="ASTM")),
                    awwa_archived=Count("id", filter=Q(is_archive=True, standard_type="AWWA")),
                    british_archived=Count("id", filter=Q(is_archive=True, standard_type="BRITISH")),
                    din_archived=Count("id", filter=Q(is_archive=True, standard_type="DIN(GERMAN)")),
                    gost_archived=Count("id", filter=Q(is_archive=True, standard_type="GOST(RUSSIAN)")),
                    iec_archived=Count("id", filter=Q(is_archive=True, standard_type="IEC")),
                    iso_archived=Count("id", filter=Q(is_archive=True, standard_type="ISO")),
                    irst_archived=Count("id", filter=Q(is_archive=True, standard_type="IRST")),
                    api_archived=Count("id", filter=Q(is_archive=True, standard_type="API")),
                    psn_archived=Count("id", filter=Q(is_archive=True, standard_type="PSN")),
                    rsn_archived=Count("id", filter=Q(is_archive=True, standard_type="RSN")),
                    ipss_archived=Count("id", filter=Q(is_archive=True, standard_type="IPSS")),
                    )
                data = {
                    "bis": standard["bis_archived"] or 0,
                    "astm": standard["astm_archived"] or 0,
                    "awwa": standard["awwa_archived"] or 0,
                    "british": standard["british_archived"] or 0,
                    "din": standard["din_archived"] or 0,
                    "gost": standard["gost_archived"] or 0,
                    "iec": standard["iec_archived"] or 0,
                    "iso": standard["iso_archived"] or 0,
                    "irst": standard["irst_archived"] or 0,
                    "api": standard["api_archived"] or 0,
                    "psn": standard["psn_archived"] or 0,
                    "rsn": standard["rsn_archived"] or 0,
                    "ipss": standard["ipss_archived"] or 0,
                }
            else:              
                standard = Standard.objects.select_related().aggregate(
                    bis_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="BIS")),
                    astm_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="ASTM")),
                    awwa_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="AWWA")),
                    british_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="BRITISH")),
                    din_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="DIN(GERMAN)")),
                    gost_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="GOST(RUSSIAN)")),
                    iec_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="IEC")),
                    iso_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="ISO")),
                    irst_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="IRST")),
                    api_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="API")),
                    psn_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="PSN")),
                    rsn_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="RSN")),
                    ipss_pending=Count("id", filter=Q(is_approved=False, is_archive=False, standard_type="IPSS")),
                    )
                data = {
                    "bis": standard["bis_pending"] or 0,
                    "astm": standard["astm_pending"] or 0,
                    "awwa": standard["awwa_pending"] or 0,
                    "british": standard["british_pending"] or 0,
                    "din": standard["din_pending"] or 0,
                    "gost": standard["gost_pending"] or 0,
                    "iec": standard["iec_pending"] or 0,
                    "iso": standard["iso_pending"] or 0,
                    "irst": standard["irst_pending"] or 0,
                    "api": standard["api_pending"] or 0,
                    "psn": standard["psn_pending"] or 0,
                    "rsn": standard["rsn_pending"] or 0,
                    "ipss": standard["ipss_pending"] or 0,
                }

            response = {
                "success": True,
                "message": f"Standard {status_type} data.",
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
