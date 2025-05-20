from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from django.contrib.auth import get_user_model
import jwt
from AdminApp.utils import Syserror
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
            # if request.META.get('HTTP_ORIGIN') != decoded_token['client']:
            #     raise AuthenticationFailed("Invalid Authentication credentials for this HTTP ORIGIN ")
            
            user_id = decoded_token["user_id"]
            user = User.objects.get(id=user_id)

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


def allowed_permission(required_permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(_, request, *args, **kwargs):
            user_permissions = request.user.user_permission  # Assuming it's a dictionary

            if request.user.role == "User" and user_permissions.get(required_permission, False):
                return Response({
                    "success": False,
                    "message": f"You do not have permission to perform this action: {required_permission}."
                }, status=400)

            return view_func(_, request, *args, **kwargs)
        
        return wrapper
    return decorator
