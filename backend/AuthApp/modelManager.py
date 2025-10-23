from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, personnel_number, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not personnel_number:
            raise ValueError(_("The Personnel Number must be set"))
        user = self.model(personnel_number=personnel_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, personnel_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser must have is_active=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        # Check if there's already a superuser
        existing_superusers = self.filter(is_superuser=True)
        if existing_superusers.exists():
            # If a superuser already exists, you can handle it as per your requirement
            # For example, you might choose to raise an exception, log a warning, or return None
            raise ValueError(_("Only one superuser is allowed."))
        return self.create_user(personnel_number, password, **extra_fields)
