from django.db import models
from django.core.validators import RegexValidator

from django.conf import settings



class SellerInfo(models.Model):
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,10}$', message="Phone number must be entered in the format: '9865656565'. without +91 ,phone number should be 10 digit long.")
    phone_number = models.CharField( max_length=17, blank=False,help_text="Please Enter contact number , without +91")
    business_name = models.CharField(max_length=255, null=True,blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'user : {self.user}'