from django.contrib import admin
from .models import Catalogue, OrderModel, Payment, Bid

# Register your models here.
admin.site.register(Catalogue)
admin.site.register(OrderModel)
admin.site.register(Payment)
admin.site.register(Bid)
