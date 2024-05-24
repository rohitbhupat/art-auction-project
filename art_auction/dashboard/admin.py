from django.contrib import admin
from dashboard.models import Catalogue,Product,OrderModel,Payment,Bid

# Register your models here.
admin.site.register([Catalogue,Product,OrderModel,Payment,Bid])
