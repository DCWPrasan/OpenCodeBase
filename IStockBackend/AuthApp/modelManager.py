from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from AdminApp.utils import encrypt_user_secret_token

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, personnel_number, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not extra_fields.get('is_superuser', False) and self.filter(is_superuser=False).count() >= settings.TOTAL_ALLOWED_USER:
            raise ValueError(_(f'Only {settings.TOTAL_ALLOWED_USER} user is allowed.'))
        if not personnel_number:
            raise ValueError(_('The Personnel Number must be set'))
        extra_fields['secret_token'] = encrypt_user_secret_token(personnel_number)
        user = self.model(personnel_number=personnel_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, personnel_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        # Check if there's already a superuser
        existing_superusers = self.filter(is_superuser=True)
        if existing_superusers.exists():
            # If a superuser already exists, you can handle it as per your requirement
            # For example, you might choose to raise an exception, log a warning, or return None
            raise ValueError(_('Only one superuser is allowed.'))
        return self.create_user(personnel_number, password, **extra_fields)
