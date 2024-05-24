from django.contrib import admin
from dashboard.models import Catalogue,Artwork,OrderModel,Payment,Bid

# Register your models here.
admin.site.register([Catalogue,Artwork,OrderModel,Payment,Bid])
