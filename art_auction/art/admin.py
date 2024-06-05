from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork
from .forms import ArtworkForm  # Import the ArtworkForm

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm
    
    fieldsets = (
        (None, {
            'fields': (
                'product_name',
                'product_price',
                'opening_bid',
                'product_cat',
                'product_id',
                'product_qty',
                'dimension_unit',
                'length_in_centimeters',
                'width_in_centimeters',
                'foot',
                'inches',
                'product_image',
                'end_date',
            )
        }),
    )

    class Media:
        js = ('js/admin_dimension_toggle.js',)
        
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If the object is being created, not edited
            obj.user = request.user
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(SellerInfo)
admin.site.register(Artwork, ArtworkAdmin)
