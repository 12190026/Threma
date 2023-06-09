# Create your models here.
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
import datetime
from cloudinary.models import CloudinaryField
from django.utils import timezone


YEAR_CHOICES = []

for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))

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
    profile_pic = CloudinaryField('profile_pics', default='profile-icon-login-head-icon-vector_teheof.jpg')
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
    STAGE_CHOICES = (
        ('Chapdro', 'Chapdro'),
        ('Semkey', 'Semkey'),
        ('Mendray', 'Mendray'),
        ('Yoenla Dinpa', 'Yoenla Dinpa'),
        ('Ku Sum Domdey', 'Ku Sum Domdey'),
        ('Lami Nyelijor', 'Lami Nyelijor'),
    )

    cid = models.CharField(primary_key=True, validators=[MinLengthValidator(11)], max_length=11)
    name = models.CharField(max_length=255)
    profile_pic = CloudinaryField('profile_pics', default='profile-icon-login-head-icon-vector_teheof.jpg')
    bob = models.DateField()
    responsibility = models.CharField(max_length=255)
    present_address = models.CharField(max_length=255)
    contact_no = models.CharField(validators=[MinLengthValidator(8)])
    village = models.CharField(max_length=255)
    card_no = models.CharField(max_length=50)
    tshogchung = models.CharField(max_length=255)
    geog = models.CharField(max_length=255)
    dzongkhag = models.CharField(max_length=255)
    stage_of_threma = models.CharField(max_length=255, choices=STAGE_CHOICES, blank=True, null=True)
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

class Activity(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),

    )

    activity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = CloudinaryField('activity_images/')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.name

class FinancialStatement(models.Model):
    year = models.PositiveIntegerField(choices=YEAR_CHOICES, unique=True)
    image = CloudinaryField('financial_statements/')

    def __str__(self):
        return str(self.year)


class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    practitioner = models.OneToOneField(Practitioner, primary_key=True, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    picture = CloudinaryField('transfer_pictures', blank=True, null=True)

    def __str__(self):
        return f"Transfer {self.practitioner.cid}: {self.practitioner.name} - {self.reason}"

    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

class Semso(models.Model):
    semso_id = models.AutoField(primary_key=True)
    date = models.DateField()
    event = models.CharField(max_length=100)
    contributor = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.event