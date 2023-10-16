from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email_address = models.EmailField(unique=True, default="example@example.com")
    firebase_uid = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
    
    
class Laundry(models.Model):
    laundryId = models.CharField(max_length=100)
    shopName = models.CharField(max_length=100)
    contactNo = models.CharField(max_length=20)
    emailAddress = models.EmailField(max_length=100)
    address = models.CharField(max_length=255)
    addressDetails = models.CharField(max_length=255)
    businessLicensePhoto = models.CharField(max_length=1000)
    fullName = models.CharField(max_length=100)
    phoneNo = models.CharField(max_length=20)
    icNo = models.CharField(max_length=20)
    registerDateTime = models.DateTimeField()
    status = models.CharField(max_length=20)
    userType = models.CharField(max_length=20)
    notification = models.BooleanField()
    setup = models.BooleanField()
    isBreak = models.BooleanField()
    balance = models.FloatField()
    ratingsAverage = models.FloatField()
    
    def __str__(self):
        return self.shopName