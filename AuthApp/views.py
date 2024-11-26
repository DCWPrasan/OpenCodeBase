# Create your views here.
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .CustomAuthBackend import AuthBackend
from django.conf import settings
from datetime import datetime, timedelta
from AdminApp.utils import Syserror
from AuthApp.models import User
from AuthApp.customAuth import JWTEncrytpToken


class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        try:
            personnel_number = request.data["personnel_number"]
            password = request.data["password"]
            user_exist = User.objects.filter(personnel_number=personnel_number).exists()
            if not user_exist:
                response = {
                    "success": False,
                    "message": "Personnel number not found",
                }
                return Response(response, status=400)
            user = AuthBackend.authenticate(request, personnel_number=personnel_number, password=password)
            if not user:
                response = {
                    "success": False,
                    "message": "Invalid Password",
                }
                return Response(response, status=400)
            if not user.is_active:
                response = {
                    "success": False,
                    "message": "Your Account is Inactive. Please contact to Owner ",
                }
                return Response(response, status=400)
            user.last_login = datetime.now()
            user.save()
            if request.META.get("HTTP_ORIGIN", None) is None:
                response = {
                    "success": False,
                    "message": "Unkonwn Client ",
                }
                return Response(response, status=400)
            jwt_payload = {
                "client": request.META["HTTP_ORIGIN"],
                "user_id": user.id,
                "iat": int(datetime.now().timestamp()),
                "exp": int(
                    (
                        datetime.now() + timedelta(seconds=settings.JWT_EXPIRE)
                    ).timestamp()
                ),
                "jti": "123456789",
                "role": user.role,
            }
            token = JWTEncrytpToken(jwt_payload)
            response = Response()
            userData = UserProfileSerializer(user).data
            resp_data = {
                "success": True,
                "message": "Login Successfully",
                "token":token,
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
                domain=settings.JWT_COOKIE_DOMAIN,  # Use your backend IP address or domain
                path="/",
            )
            response.status_code = 200
            response['Access-Control-Allow-Origin']=request.headers.get('Origin', '')
            return response
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class Logout(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

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
                domain=settings.JWT_COOKIE_DOMAIN, 
                path="/",
            )
            response.status_code = 200
            response['Access-Control-Allow-Origin']=request.headers.get('Origin', '')
            return response
        except Exception as e:
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
            name = data.get("name", None)
            password = data.get("password", None)
            user = request.user
            user.name = name
            if password:
                user.set_password(password)
            user.save()
            resp_data = UserProfileSerializer(user).data
            response = {
                "success": True,
                "message": "User Profile Updated",
                "data": resp_data,
            }
            return Response(response, status=200)
        except Exception as e:
            print(e)
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
            if new_password == password:
                response = {"success": False, "message": "Please enter different new password"}
                return Response(response, status=400)
            user = request.user
            if user.check_password(password):
                user.set_password(new_password)
                user.save()
                resp_data = UserProfileSerializer(user).data
                response = {
                    "success": True,
                    "message": "User Password update successfully.",
                    "data": resp_data,
                }
                return Response(response, status=200)
            else:
                response = {"success": False, "message": "Invalid current password"}
                return Response(response, status=400)
        except Exception as e:
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

