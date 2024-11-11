from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# baseclass
class BaseClass(models.Model):
    uuid=models.SlugField(default=uuid.uuid4,unique=True)
    active_status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class RoleChoices(models.TextChoices):
    ADMIN = 'Admin', 'Admin' 

## Profile model 
class Profile(AbstractUser):
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    role=models.CharField(max_length=15,choices=RoleChoices.choices)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15,null=True,blank=True)
    phone_b=models.CharField(max_length=15,null=True,blank=True)
    email_verified=models.BooleanField(default=False)
    phone_verified=models.BooleanField(default=False)
    address_line1=models.TextField(null=True,blank=True)
    address_line2=models.TextField(null=True,blank=True)
    city=models.CharField(max_length=255,null=True,blank=True)
    state=models.CharField(max_length=30,null=True,blank=True)
    zip_code=models.CharField(max_length=8,null=True,blank=True)



    def __str__(self):
        return f'{self.email} ,-- {self.role}'
    
    class Meta:
        ordering=['-id']
        verbose_name='Profile'
        verbose_name_plural='Profile'


class ComapanyInfo(BaseClass):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    address_line1=models.CharField(max_length=255,null=True,blank=True)
    address_line2=models.CharField(max_length=255,null=True,blank=True)
    phone=models.CharField(max_length=12,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    licence_name=models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return 'company info'