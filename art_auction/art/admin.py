from django.contrib import admin
from art.models import SellerInfo
from dashboard.models import Artwork
from .forms import ArtworkForm  # Import the ArtworkForm

class ArtworkAdmin(admin.ModelAdmin):
    form = ArtworkForm

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
        kwargs['form'] = ArtworkForm
        form = super().get_form(request, obj=obj, **kwargs)
        if obj:  # When editing an existing object
            form.base_fields['sale_type'].initial = obj.sale_type
        else:  # When adding a new object
            form.base_fields['sale_type'].initial = 'bidding'  # Default value
        return form

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically adjust the fieldsets based on the sale_type of the Artwork.
        """
        if obj and obj.sale_type == 'discount':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'product_price',
                        'product_qty', 'product_image', 'is_sold', 'is_purchased', 'created_at',
                    )
                }),
            )
        elif obj and obj.sale_type == 'bidding':
            return (
                (None, {
                    'fields': (
                        'sale_type', 'product_name', 'opening_bid', 'product_cat',
                        'product_qty', 'product_image', 'end_date', 'is_sold', 'is_purchased', 'created_at',
                    )
                }),
            )
        return super().get_fieldsets(request, obj)

    # Exclude 'discounted_price' field from the admin form
    exclude = ('discounted_price',)

# Register your models here.
admin.site.register(SellerInfo)
admin.site.register(Artwork, ArtworkAdmin)