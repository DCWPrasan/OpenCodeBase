from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def authenticate(self, personnel_number=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(personnel_number=personnel_number)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
