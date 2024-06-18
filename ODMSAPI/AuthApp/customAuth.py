from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from django.contrib.auth import get_user_model
import jwt
from core.utility import Syserror
from django.conf import settings
from functools import wraps
from rest_framework.response import Response

# custom_auth.py


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get(settings.JWT_TOKEN_NAME)
        if not token:
            if authtoken := request.headers.get('Authorization', None):
                token = authtoken.split(' ')[1]
        User = get_user_model()
        if not token:
            raise NotAuthenticated("Authentication credentials were not provided.")

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = decoded_token["user_id"]
            user = User.objects.get(id=user_id)

            if user.jti_token != decoded_token["jti"]:
                raise AuthenticationFailed("This account was login with another device")

        except jwt.ExpiredSignatureError:
            raise NotAuthenticated("Authentication credentials were expried.")

        except jwt.InvalidTokenError:
            raise NotAuthenticated(
                "Incorrect Authentication credentials were provided."
            )
        except User.DoesNotExist:
            raise AuthenticationFailed("No such user exists")
        except Exception as e:
            Syserror(e)
            raise AuthenticationFailed(str(e))
        return (user, None)


def JWTEncrytpToken(payload):
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)



def allowed_superadmin(view_func):
    @wraps(view_func)
    def wrapper(_, request, *args, **kwargs):
        if request.user.role != "SuperAdmin":
            return Response({"success": False, "message": "You do not have permission to access this resource."}, status=400)
        return view_func(_, request, *args, **kwargs)
    return wrapper

def allowed_admin_user(view_func):
    @wraps(view_func)
    def wrapper(_, request, *args, **kwargs):
        if request.user.role not in ["SuperAdmin", "Admin"]:
            return Response({"success": False, "message": "You do not have permission to access this resource."}, status=400)
        return view_func(_, request, *args, **kwargs)
    return wrapper