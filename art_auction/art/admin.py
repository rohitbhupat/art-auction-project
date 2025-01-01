from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork
from .forms import ArtworkForm  # Import the ArtworkForm

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm

    class Media:
        js = ('js/admin_dimension_toggle.js',)

    def save_model(self, request, obj, form, change):
        if obj.sale_type == 'discount' and obj.product_price:
            obj.discounted_price = obj.product_price * 0.7  # Apply 30% discount
            print(f"Discounted Price: {obj.discounted_price}")  # Debugging

        if obj.user is None:
            obj.user = request.user

        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = ArtworkForm
        form = super().get_form(request, obj=obj, **kwargs)
        if obj:  # When editing an existing object
            form.base_fields['sale_type'].initial = obj.sale_type
        else:  # When adding a new object
            form.base_fields['sale_type'].initial = 'auction'  # Default value
        return form

    def get_fieldsets(self, request, obj=None):
        if obj and obj.sale_type == 'discount':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'product_price', 'discounted_price',
                        'product_qty', 'product_image', 'dimension_unit', 
                        'length_in_centimeters', 'width_in_centimeters', 
                        'foot', 'inches', 'created_at'
                    )
                }),
            )
        elif obj and obj.sale_type == 'auction':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'opening_bid', 'product_cat',
                        'product_qty', 'product_image', 'end_date', 
                        'dimension_unit', 'length_in_centimeters', 'width_in_centimeters', 
                        'foot', 'inches', 'created_at'
                    )
                }),
            )
        return super().get_fieldsets(request, obj)

    # exclude = ('discounted_price',)
    # Exclude 'discounted_price' field from the admin form if needed
admin.site.register(Artwork, ArtworkAdmin)
admin.site.register(SellerInfo)