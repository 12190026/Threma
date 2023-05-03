# Create your models here.
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser

class ExecutiveMemberManager(BaseUserManager):
    def create_user(self, cid, password=None, role=None, **extra_fields):
        """
        Creates and saves a ExecutiveMember with the given cid and password.
        """
        if not cid:
            raise ValueError('The CID field must be set')
        user = self.model(cid=cid, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, cid, password, role=None, **extra_fields):
        """
        Creates and saves a superuser with the given cid and password.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(cid, password, role, **extra_fields)

class ExecutiveMember(AbstractBaseUser, PermissionsMixin):
   
    ROLE_CHOICES = (
        ('MANAGER', 'Manager'),
        ('CHAIRPERSON', 'Chairperson'),
        ('TREASURER', 'Treasurer'),
        ('ADMIN', 'Admin'),
    )

    cid = models.CharField(max_length=11, unique=True, validators=[MinLengthValidator(11)])
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    responsibility = models.CharField(max_length=255)
    present_address = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    card_no = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    geog = models.CharField(max_length=255)
    dzongkhag = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = ExecutiveMemberManager()

    USERNAME_FIELD = 'cid'
    REQUIRED_FIELDS = ['name', 'role', 'email', ]

    def __str__(self):
        return self.cid

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        verbose_name = 'Executive Member'
        verbose_name_plural = 'Executive Members'



class Practitioner(AbstractBaseUser):
    cid = models.CharField(max_length=11, unique=True, validators=[MinLengthValidator(11)])
    name = models.CharField(max_length=255)
    responsibility = models.CharField(max_length=255)
    present_address = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    card_no = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    geog = models.CharField(max_length=255)
    dzongkhag = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'cid'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.cid

    @property
    def password(self):
        return None

    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        return False
