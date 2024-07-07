from django.contrib import admin
from .models import Catalogue, OrderModel, Payment, Bid, Query, Notification

# Register your models here.
admin.site.register(Catalogue)
admin.site.register(OrderModel)
admin.site.register(Payment)
admin.site.register(Bid)
admin.site.register(Query)
admin.site.register(Notification)


class QueryAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'query_description')
    search_fields = ('first_name', 'last_name', 'email')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username', 'message')