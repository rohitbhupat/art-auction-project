from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork
from .forms import ArtworkForm  # Import the ArtworkForm

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm
    
    fieldsets = (
        (None, {
            'fields': (
                'sale_type', 'product_name', 'product_price', 'opening_bid',
                'product_cat', 'product_id', 'product_qty', 'dimension_unit',
                'length_in_centimeters', 'width_in_centimeters', 'foot', 'inches',
                'product_image', 'end_date', 'is_sold', 'is_purchased', 'created_at',
            )
        }),
    )

    class Media:
        js = ('js/admin_dimension_toggle.js',)
        
    def save_model(self, request, obj, form, change):
        # Custom logic for discount calculations
        if obj.sale_type == 'discount' and obj.product_price:
            obj.discounted_price = obj.product_price * 0.7  # Apply 30% discount
            
        if obj.user is None:  # Assign the user to the artwork if not specified
            obj.user = request.user
            
        print(f"Saving Artwork: {obj.product_name}, Sale Type: {obj.sale_type}, Dimensions: {obj.dimension_unit}")
        super().save_model(request, obj, form, change)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        initial = {'sale_type': obj.sale_type if obj else 'bidding'}
        return form(request=request, initial=initial)

# Register your models here.
admin.site.register(SellerInfo)
admin.site.register(Artwork, ArtworkAdmin)
