# Create your views here.
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
from AdminApp.utils import Syserror, decrypt_user_secret_token
from AuthApp.customAuth import JWTEncrytpToken
from AuthApp.models import LogInOutLog

def parse_user_agent(request):
    # Initialize variables for OS, browser, and device
    os = ''
    browser = ''
    device = ''
    user_agent_string = request.META.get('HTTP_USER_AGENT', None)
    # Detect operating system
    if 'Windows' in user_agent_string:
        os = 'Windows'
    elif 'Linux' in user_agent_string:
        os = 'Linux'
    elif 'Macintosh' in user_agent_string:
        os = 'Macintosh'
    elif 'Android' in user_agent_string:
        os = 'Android'
    elif 'iOS' in user_agent_string:
        os = 'iOS'
    # Add more conditions for other operating systems as needed
    # Detect browser
    if 'Chrome' in user_agent_string:
        browser = 'Chrome'
    elif 'Firefox' in user_agent_string:
        browser = 'Firefox'
    elif 'Safari' in user_agent_string:
        browser = 'Safari'
    elif 'Edge' in user_agent_string:
        browser = 'Edge'
    elif 'Opera' in user_agent_string:
        browser = 'Opera'
    # Add more conditions for other browsers as needed
    # Detect device
    if 'Mobile' in user_agent_string:
        device = 'Mobile'
    elif 'Tablet' in user_agent_string:
        device = 'Tablet'
    elif 'Windows NT' in user_agent_string:  # Assuming it's a desktop if not Mobile or Tablet
        device = 'Desktop'
    # Add more conditions for other devices as needed
    client_ip = request.META.get('REMOTE_ADDR', None)
    # If REMOTE_ADDR is not available, try X-Forwarded-For header (commonly used when behind proxies)
    if not client_ip:
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
        client_ip = client_ip.split(',')[0].strip()
    return f"{f'OS-{os}' if os else''} {f'Browser-{browser}' if browser else''} {f'Device-{device}' if device else''} {f'IP-{client_ip}' if client_ip else ''}"



class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        try:
            personnel_number = request.data["personnel_number"]
            password = request.data["password"]
            user_exist = Users.objects.filter(Q(personnel_number=personnel_number) | Q(email=personnel_number))
            if not user_exist.exists():
                response = {
                    "success": False,
                    "message": "Personnel number or Email not found",
                }
                return Response(response, status=400)
            user = user_exist.first()
            if not user.check_password(password):
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
            if request.META["HTTP_ORIGIN"] is None:
                response = {
                    "success": False,
                    "message": "Inavlid request Client ",
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
            device_info = parse_user_agent(request)
            LogInOutLog.objects.create(
                user=user,
                message="Login",
                details="User Login",
                device_info=device_info,
            )
            token = JWTEncrytpToken(jwt_payload)
            response = Response()
            userData = CustomerLoginDataDataSerializer(user).data
            resp_data = {
                "success": True,
                "message": "Login Successfully",
                "data": userData,
                "token":token
            }
            response = Response(resp_data)
            response.set_cookie(
                settings.JWT_TOKEN_NAME,
                token,
                max_age=settings.JWT_EXPIRE,
                httponly=True,
                secure=settings.JWT_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path="/",
            )
            response.status_code = 200
            return response
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class Logout(APIView):
    # permission_classes = (AllowAny,)
    # authentication_classes = []

    def get(self, request):
        try:
            response = Response()
            response.set_cookie(
                settings.JWT_TOKEN_NAME,
                "",
                max_age=0,
                httponly=True,
                secure=settings.JWT_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path="/",
            )
            device_info = parse_user_agent(request)
            if user := request.user:
                LogInOutLog.objects.create(
                    user=user,
                    message="Logout",
                    details="User Logout",
                    device_info=device_info,
                )
            response.data = {
                "success": True,
                "message": "Logout successfully",
            }
            response.status_code = 200
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
            userData = CustomerLoginDataDataSerializer(user).data
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
            resp_data = CustomerLoginDataDataSerializer(user).data
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
            resp_data = CustomerLoginDataDataSerializer(user).data
            response = {
                "success": True,
                "message": "User Profile Updated",
                "data": resp_data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


# class UserNewRefreshToken(APIView):
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         print("RToken Called ------->>", request.data.get("refresh"))
#         try:
#             token = request.data.get("refresh")
#             token_decode = jwt.decode(
#                 token,
#                 settings.SIMPLE_JWT["SIGNING_KEY"],
#                 algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
#             )
#             exp_time = datetime.fromtimestamp(int(token_decode["exp"]))
#             user_id = token_decode["user_id"]
#             if exp_time > datetime.now():
#                 user = Users.objects.get(id=user_id)
#                 token = RefreshToken(token)
#                 token.blacklist()
#                 refresh = MyTokenObtainPairSerializer.get_token(user)
#                 access_token = str(refresh.access_token)
#                 refresh_token = str(refresh)
#                 response = {
#                     "success": True,
#                     "message": "New Token Get Successfully",
#                     "access_token": access_token,
#                     "refresh_token": refresh_token,
#                 }
#                 return Response(response, status=200)
#             else:
#                 response = {
#                     "success": False,
#                     "message": "Refresh_Token Is not Valid",
#                 }
#                 return Response(response, status=401)
#         except Exception as e:
#             Syserror(e)
#             response = {
#                 "success": False,
#                 "message": str(e),
#             }
#             return Response(response, status=400)
