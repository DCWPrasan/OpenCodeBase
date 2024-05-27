import os
from rest_framework.views import APIView
from .serializers import NoticeSerializer, SliderSerializer, NewUserRequestSerializer
from AuthApp.pagination import CustomPagination
from .models import Notice, Slider, NewUserRequest
from django.db.models import Q
from rest_framework.response import Response
from core.utility import Syserror
from AuthApp.customAuth import allowed_admin_user
from django.db import transaction
from rest_framework.permissions import AllowAny
import re
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile




# notice
class NoticeApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = NoticeSerializer
    
    def get(self, request, id=None):
        try:
            filter_criteria = Q()
            if id:
                try:
                    filter_criteria &= Q(id=id)
                    instance = Notice.objects.get(filter_criteria)
                except Notice.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Notice doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Notice data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q()
                if is_publish := request.GET.get("publish", None):
                    if is_publish == "YES":
                        filter_criteria &= Q(is_published=True)
                    elif is_publish == "NO":
                        filter_criteria &= Q(is_published=False)
                if query := request.GET.get("query"):
                    filter_criteria &= Q(
                        Q(title__icontains=query)
                        | Q(description__icontains=query)
                    )
                instance = Notice.objects.filter(filter_criteria).order_by("-created_at")
                                
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)
                
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Notice data retrieved successfully."
                }
                return Response(response, status=200)
                        
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=200)
    
    @allowed_admin_user
    def post(self, request):
        try:
            data = request.data
            title = data.get("title", None) or None
            description = data.get("description", None) or None
            is_published = data.get("is_published", "NO") == "YES"
            
            if not all([title, description]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            with transaction.atomic():
                instance = Notice.objects.create(
                    title = title,
                    description = description,
                    is_published = is_published
                )
                instance.save()
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Notice created successfully.",
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
            title = data.get("title", None) or None
            description = data.get("description", None) or None
            is_published = data.get("is_published", "NO") == "YES"
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required id"
                }
                return Response(response, status=400)
            
            if not all([title, description]):
                response = {
                    "success": False,
                    "message": "All the mandatory fields are required."
                }
                return Response(response, status=400)
            
            instance = Notice.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Notice not found."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance.title = title
                instance.description = description
                instance.is_published = is_published
                instance.save()
                
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Notice updated successfully.",
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
    def delete(self, request, id=None):
        try:
            if id:
                try:
                    instance = Notice.objects.get(id=id)
                except Notice.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Notice doesn't exist."
                    }
                    return Response(response, status=400)
                instance.delete()
                
            
                response = {
                    "success": True,
                    "message": "Notice deleted successfully."
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)
            

class NoticeOpenApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        try:
            instance = Notice.objects.filter(is_published=True).order_by("-created_at")[:25]
            serializer = NoticeSerializer(instance, many=True)
            response = {
                "success": True,
                "message": "Notice data retrieved successfully.",
                "results": serializer.data
            }
            return Response(response, status=200)
                        
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=200)


# slider
class SliderApiView(APIView):
    pagination_class = CustomPagination
    serializer_class = SliderSerializer
    
    def get(self, request, id=None):
        try:
            filter_criteria = Q()
            if id:
                try:
                    filter_criteria &= Q(id=id)
                    instance = Slider.objects.get(filter_criteria)
                except Slider.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Slider doesn't exist."
                    }
                    return Response(response, status=400)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Slider data retrieved successfully.",
                    "results": serializer.data
                }
                return Response(response, status=200)
            else:
                filter_criteria = Q()
                if is_publish := request.GET.get("publish", None):
                    if is_publish == "YES":
                        filter_criteria &= Q(is_published=True)
                    elif is_publish == "NO":
                        filter_criteria &= Q(is_published=False)
                instance = Slider.objects.filter(filter_criteria).order_by("-created_at")
                
                paginator = self.pagination_class()
                page = paginator.paginate_queryset(instance, request, view=self)
                
                if page is not None:
                    serializer = self.serializer_class(page, many=True)
                    result = paginator.get_paginated_response(serializer.data)
                    return result
                
                serializer = self.serializer_class(instance, many=True)
                response = {
                    "success": True,
                    "message": "Slider data retrieved successfully.",
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
            media = data.get("media", None) or None
            is_published = data.get("is_published", "NO") == "YES"

            if not media:
                response = {
                    "success": False,
                    "message": "Required media file."
                }
                return Response(response, status=400)
            else:
                is_file_valid = isinstance(media, InMemoryUploadedFile) or isinstance(media, UploadedFile)
                if not is_file_valid:
                    response = {
                        "success": False,
                        "message": "Upload valid file."
                    }
                    return Response(response, status=400)
                file_ext = media.name.split(".")[-1].upper()
                if file_ext not in ["JPG", "JPEG", "PNG","MP4"]:    # checking file extension
                    response = {
                        "success": False,
                        "message": "File must be .jpg/.jpeg/.png or .mp4."
                    }
                    return Response(response, status=400)
            
            with transaction.atomic():
                instance = Slider.objects.create(
                    media = media,
                    is_published = is_published
                )
                instance.save()
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Slider created successfully.",
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
            is_published = data.get("is_published", "NO") == "YES"
            
            if not id:
                response = {
                    "success": False,
                    "message": "Required id"
                }
                return Response(response, status=400)
            
            instance = Slider.objects.filter(id=id).first()
            if instance is None:
                response = {
                    "success": False,
                    "message": "Slider not found."
                }
                return Response(response, status=400)
            
            with transaction.atomic():
                instance.is_published = is_published
                instance.save()
                
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Slider updated successfully.",
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
    def delete(self, request, id=None):
        try:
            if id:
                try:
                    instance = Slider.objects.get(id=id)
                except Slider.DoesNotExist:
                    response = {
                        "success": False,
                        "message": "Slider doesn't exist."
                    }
                    return Response(response, status=400)
                
                # attachment deletion will handle by model signal
                instance.delete()
            
                response = {
                    "success": True,
                    "message": "Slider deleted successfully."
                }
                return Response(response, status=200)
            else:
                response = {
                    "success": False,
                    "message": "Required ID."
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e)
            }
            return Response(response, status=400)


class SliderOpenApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        try:
            instance = Slider.objects.filter(is_published=True).order_by("-created_at")[:25] 
            serializer = SliderSerializer(instance, many=True)
            response = {
                "success": True,
                "message": "Slider data retrieved successfully.",
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
        

# Create your views here.
class NewUserReuqestApiView(APIView):
    pagination_class = CustomPagination  # Set the custom pagination class
    serializer_class = NewUserRequestSerializer

    @allowed_admin_user
    def get(self, request):
        try:
            # retrive list of user object according to filter_criteria
            filter_criteria = Q()
            if query := request.GET.get("query"):
                filter_criteria &= Q(
                    Q(full_name__icontains=query)
                    | Q(email__icontains=query)
                    | Q(personnel_number__icontains=query)
                    | Q(phone_number__icontains=query)
                    | Q(department__icontains=query)
                    | Q(cost_code_department__icontains=query)
                    | Q(designation__icontains=query)
                )

            instance = NewUserRequest.objects.filter(filter_criteria).order_by("-created_at")

            # Paginate the results using the custom pagination class
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
        
class CreateNewUserRequestApiView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = NewUserRequestSerializer
    def get(self, request, personnel_number):
        try:
            instance = NewUserRequest.objects.filter(personnel_number = personnel_number)
            if instance:
                serializer = self.serializer_class(instance.first())
                return Response({"results": serializer.data}, status=200)
            else:
                response = {"success": False, "message": "Personnel Number not found!"}
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)
    def post(self, request):
        try:
            data = request.data
            full_name = data.get("full_name", None)
            email = data.get("email", None)
            phone_number = data.get("phone_number", None)
            personnel_number = data.get("personnel_number", None)
            department = data.get("department", None)
            cost_code_department = data.get("cost_code_department", None)
            designation = data.get("designation", None)
            if not all(
                [
                    full_name,
                    personnel_number,
                    email,
                    phone_number,
                    department,
                    cost_code_department,
                    designation
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

            if not str(phone_number).isdigit() or len(str(phone_number)) != 10:
                response = {
                    "success": False,
                    "message": "Invalid phone number, require 10 digits.",
                }
                return Response(response, status=400)

            if NewUserRequest.objects.filter(email=email).exists():
                response = {
                    "success": False,
                    "message": "Email already exists.",
                }
                return Response(response, status=400)
            if NewUserRequest.objects.filter(phone_number=phone_number).exists():
                response = {
                    "success": False,
                    "message": "Phone number already exists.",
                }
                return Response(response, status=400)
            if NewUserRequest.objects.filter(personnel_number=personnel_number).exists():
                response = {
                    "success": False,
                    "message": "Personnel number already exists.",
                }
                return Response(response, status=400)
            with transaction.atomic():
                instance = NewUserRequest.objects.create(
                    full_name=full_name,
                    email=email,
                    phone_number=phone_number,
                    personnel_number=personnel_number,
                    department=department,
                    cost_code_department=cost_code_department,
                    designation=designation,
                )
                response = {
                    "success": True,
                    "message": "Request submitted successfully.",
                    "results": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

            
