# Create your views here.
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .CustomAuthBackend import AuthBackend
from django.conf import settings
from datetime import datetime, timedelta
from core.utility import Syserror, getId, parse_user_agent, get_file_name_and_extension
from AuthApp.models import User, LogInOutLog
from AuthApp.customAuth import JWTEncrytpToken
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
import os
import re

class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        try:
            data = request.data
            personnel_number = data.get("personnel_number", None)
            password = data.get("password", None)
            if not personnel_number:
                response = {"success": False, "message": "Required personnel number."}
                return Response(response, status=400)
            if not password:
                response = {"success": False, "message": "Required password."}
                return Response(response, status=400)

            user_exist = User.objects.filter(personnel_number=personnel_number)
            if not user_exist.exists():
                response = {"success": False, "message": "Personnel number not found."}
                return Response(response, status=400)

            if not user_exist.first().is_active:
                response = {
                    "success": False,
                    "message": "Your Account is Inactive. Please contact admin.",
                }
                return Response(response, status=400)

            user = AuthBackend.authenticate(
                request, personnel_number=personnel_number, password=password
            )
            if not user:
                response = {
                    "success": False,
                    "message": "Invalid Password",
                }
                return Response(response, status=400)

            if request.META.get("HTTP_ORIGIN", None) is None:
                response = {
                    "success": False,
                    "message": "Unkonwn Client , Required HTTP_ORIGIN",
                }
                return Response(response, status=400)
            jti_token = getId()
            while User.objects.filter(jti_token=jti_token).exists():
                jti_token = getId()

            jwt_payload = {
                "client": request.META["HTTP_ORIGIN"],
                "user_id": user.id,
                "iat": int(datetime.now().timestamp()),
                "exp": int(
                    (
                        datetime.now() + timedelta(seconds=settings.JWT_EXPIRE)
                    ).timestamp()
                ),
                "jti": jti_token,
                "role": user.role,
            }
            device_info = parse_user_agent(request)
            if user.jti_token:
                if user.jti_token != jti_token:
                    user.last_logout = datetime.now()
                    LogInOutLog.objects.create(
                        user=user,
                        message="Logout",
                        details="User Logout",
                        device_info=device_info,
                    )
            user.last_login = datetime.now()
            user.jti_token = jti_token
            user.save()
            token = JWTEncrytpToken(jwt_payload)
            LogInOutLog.objects.create(
                user=user,
                message="Login",
                details="User Login",
                device_info=device_info,
            )
            response = Response()
            userData = UserProfileSerializer(user).data
            resp_data = {
                "success": True,
                "message": "Login Successfully",
                "token": token,
                "data": userData,
            }
            response = Response(resp_data)
            response.set_cookie(
                settings.JWT_TOKEN_NAME,
                token,
                max_age=settings.JWT_EXPIRE,
                httponly=True,
                secure=settings.JWT_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                # domain=settings.JWT_COOKIE_DOMAIN,  # Use your backend IP address or domain
                path="/",
            )
            response.status_code = 200
            response["Access-Control-Allow-Origin"] = request.headers.get("Origin", "")
            return response
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class Logout(APIView):
    # permission_classes = (AllowAny, IsAuthenticated)
    # authentication_classes = []

    def get(self, request):
        try:
            response = Response()
            response.data = {
                "success": True,
                "message": "Logout successfully",
            }
            response.set_cookie(
                settings.JWT_TOKEN_NAME,
                "",
                max_age=0,
                httponly=True,
                secure=settings.JWT_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                # domain=settings.JWT_COOKIE_DOMAIN,  # Use your backend IP address or domain
                path="/",
            )
            response.status_code = 200
            response["Access-Control-Allow-Origin"] = request.headers.get("Origin", "")
            if user := request.user:
                device_info = parse_user_agent(request)
                LogInOutLog.objects.create(
                    user=user,
                    message="Logout",
                    details="User Logout",
                    device_info=device_info,
                )
                user.jti_token = None
                user.save()
            return response
        except Exception as e:
            Syserror(e)
            response = {
                "success": "false",
                "message": str(e),
            }
            return Response(response, status=400)


class UserLoginCheck(APIView):
    def get(self, request):
        try:
            user = request.user
            if not user:
                raise ValueError("User Not Authorized")
            user.last_login = datetime.now()
            user.save()
            userData = UserProfileSerializer(user).data
            resp_data = {"success": True, "message": "User login", "data": userData}
            return Response(resp_data, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UserProfileView(APIView):
    def get(self, request):
        try:
            user = request.user
            resp_data = UserProfileSerializer(user).data
            response = {
                "success": True,
                "message": "Customer Details",
                "data": resp_data,
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def post(self, request):
        try:
            data = request.data
            file = data.get("profile_photo", None)
            is_file_list_valid = isinstance(file, InMemoryUploadedFile) or isinstance(
                file, UploadedFile
            )
            if not is_file_list_valid:
                response = {
                    "success": False,
                    "message": "choose a valid file",
                }
                return Response(response, status=400)
            _, extension = get_file_name_and_extension(file.name)

            if extension not in ["JPG", "JPEG", "PNG"]:
                response = {
                    "success": False,
                    "message": "invalid file extension",
                }
                return Response(response, status=400)

            user = request.user
            pp_path = None
            if user.profile_photo:
                pp_path = user.profile_photo.path
            user.profile_photo = file
            user.save()
            if pp_path and os.path.isfile(pp_path):
                os.remove(pp_path)

            response = {
                "success": True,
                "message": "User profile photo updated successfully.",
                "results": user.profile_photo.url,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            data = request.data
            new_password = data.get("new_password", None)
            password = data.get("current_password", None)
            if not ([new_password, password]):
                response = {"success": False, "message": "All the mandatory fields are required"}
                return Response(response, status=400)
            user = request.user
            if user.check_password(password):
                user.set_password(new_password)
                user.jti_token = None
                device_info = parse_user_agent(request)
                LogInOutLog.objects.create(
                    user=user,
                    message="Logout",
                    details="User Logout (change password)",
                    device_info=device_info,
                )
            user.save()
            resp_data = UserProfileSerializer(user).data
            response = {
                "success": True,
                "message": "User Password update successfully.",
                "data": resp_data,
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)
        
    def patch(self, request):
        try:
            data = request.data
            email = data.get("email", None)
            phone_number = data.get("phone_number", None)
            designation = data.get("designation", None)
            if not ([email, phone_number, designation]):
                response = {"success": False, "message": "All the mandatory fields are required"}
                return Response(response, status=400)
            user = request.user
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
            if User.objects.filter(email=email).exclude(email=user.email).exists():
                response = {"success": False, "message": "Email already exists."}
                return Response(response, status=400)
            if User.objects.filter(phone_number=phone_number).exclude(phone_number=user.phone_number).exists():
                response = {"success": False, "message": "Phone number already exists."}
                return Response(response, status=400)
            user.email = email
            user.phone_number = phone_number
            user.designation = designation
            user.save()
            resp_data = UserProfileSerializer(user).data
            response = {
                "success": True,
                "message": "User Password update successfully.",
                "data": resp_data,
            }
            return Response(response, status=200)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

