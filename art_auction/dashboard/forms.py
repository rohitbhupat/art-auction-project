from django import forms
from .models import Artwork  # Adjust import paths if necessary
from PIL import Image
import imagehash

class ArtworkCreateForm(forms.ModelForm):
    sale_type = forms.ChoiceField(
        choices=[('discount', 'Discount'), ('auction', 'Auction')],
        widget=forms.RadioSelect,
        required=False,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Auction End Date"
    )

    class Meta:
        model = Artwork
        fields = [
            "product_name", "product_price", "opening_bid", "product_cat",
            "product_qty", "dimension_unit", "length_in_centimeters", "width_in_centimeters",
            "foot", "inches", "product_image", "end_date"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sale_type = self.initial.get('sale_type', 'auction')
        
        if sale_type == 'discount':
            # Hide fields for discount sale type
            self.fields['opening_bid'].widget = forms.HiddenInput()
            self.fields['end_date'].widget = forms.HiddenInput()
        else:
            # Make these fields required for auction sale type
            self.fields['opening_bid'].required = True
            self.fields['end_date'].required = True

    def clean(self):
        cleaned_data = super().clean()
        sale_type = cleaned_data.get('sale_type', 'auction')  # Default to 'auction'
        
        cleaned_data['sale_type'] = sale_type  # Ensure sale_type is saved

        if sale_type == 'discount':
            cleaned_data['opening_bid'] = None
            cleaned_data['end_date'] = None
            if not cleaned_data.get('product_price'):
                self.add_error('product_price', "Product price is required for discounts.")
        elif sale_type == 'auction':
            if not cleaned_data.get('opening_bid'):
                self.add_error('opening_bid', "Opening bid is required for auctions.")
            if not cleaned_data.get('end_date'):
                self.add_error('end_date', "End date is required for auctions.")
    
        return cleaned_data


class ArtworkUpdateForm(forms.ModelForm):
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Auction End Date"
    )

    class Meta:
        model = Artwork
        fields = [
            "product_name", "product_price", "product_image", 
            "product_cat", "end_date", "length_in_centimeters", 
            "width_in_centimeters", "foot", "inches"
        ]

    def clean_product_image(self):
        # Duplicate image detection logic
        uploaded_image = self.cleaned_data.get('product_image')
        if uploaded_image:
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.exclude(id=self.instance.id)

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(Image.open(artwork.product_image.path))
                if uploaded_image_hash == stored_image_hash:
                    raise forms.ValidationError("Duplicate image detected. This artwork has already been uploaded.")
        return uploaded_image