from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork
from .forms import ArtworkForm  # Import the ArtworkForm

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm
    
    list_display = ("product_name", "sale_type", "product_price", "purchase_category", "is_sold")
    list_filter = ("sale_type", "purchase_category", "is_sold")
    search_fields = ("product_name", "purchase_category__name") 

    class Media:
        js = ('js/admin_dimension_toggle.js',)  # Ensure the path is correct

    def save_model(self, request, obj, form, change):
        if obj.sale_type == 'discount' and obj.product_price:
            obj.discounted_price = obj.product_price * 0.7  # Apply 30% discount
            print(f"Discounted Price: {obj.discounted_price}")  # Debugging

        if not obj.user:
            obj.user = request.user

        super().save_model(request, obj, form, change)

    def get_changeform_initial_data(self, request):
        """Set default values when adding a new artwork."""
        return {'sale_type': 'auction'}

    def get_fieldsets(self, request, obj=None):
        if obj and obj.sale_type == 'discount':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'purchase_category', 'product_price', 'discounted_price',
                        'product_qty', 'product_image', 'dimension_unit', 
                        'length_in_centimeters', 'width_in_centimeters', 
                        'foot', 'inches',
                    )
                }),
            )
        elif obj and obj.sale_type == 'auction':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'opening_bid', 'product_cat', 'purchase_category', # <-- Add this
                        'product_qty', 'product_image', 'end_date', 
                        'dimension_unit', 'length_in_centimeters', 'width_in_centimeters', 
                        'foot', 'inches',
                    )
                }),
            )
    
        return super().get_fieldsets(request, obj)

admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(SellerInfo)