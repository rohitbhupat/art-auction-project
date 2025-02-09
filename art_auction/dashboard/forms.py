from django import forms
from .models import Artwork, PurchaseCategory  # Adjust import paths if necessary
from PIL import Image
import imagehash


class ArtworkCreateForm(forms.ModelForm):
    sale_type = forms.ChoiceField(
        choices=[("discount", "Discount"), ("auction", "Auction")],
        widget=forms.RadioSelect,
        required=False,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Auction End Date",
    )

    class Meta:
        model = Artwork
        exclude = ["user", "is_sold", "is_purchased", "status", "response_deadline", "buyer_response"]
        fields = [
            "product_name",
            "product_price",
            "opening_bid",
            "product_cat",
            "product_qty",
            "dimension_unit",
            "length_in_centimeters",
            "purchase_category",
            "width_in_centimeters",
            "foot",
            "inches",
            "product_image",
            "end_date",
            "discounted_price",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sale_type = kwargs.get('data', {}).get('sale_type') or self.initial.get('sale_type')

        # Ensure dropdown appears for discount artworks
        if sale_type == "discount":
            self.fields["purchase_category"].widget = forms.Select(
                choices=[(cat.id, cat.name) for cat in PurchaseCategory.objects.all()]
            )
            self.fields["purchase_category"].required = True
        else:
            self.fields["purchase_category"].widget = forms.HiddenInput()
            self.fields["purchase_category"].required = False

    def clean(self):
        cleaned_data = super().clean()
        sale_type = cleaned_data.get("sale_type", "discount")

        if sale_type == "auction":
            cleaned_data["purchase_category"] = None  # Ensure it's removed
            if not cleaned_data.get("opening_bid"):
                self.add_error("opening_bid", "Opening bid is required for auctions.")
            if not cleaned_data.get("end_date"):
                self.add_error("end_date", "End date is required for auctions.")

        elif sale_type == "discount":
            cleaned_data["opening_bid"] = None  # Ensure it's cleared
            cleaned_data["end_date"] = None
            if not cleaned_data.get("discounted_price"):
                cleaned_data["discounted_price"] = cleaned_data.get("product_price", 0) * 0.7

            if not cleaned_data.get("purchase_category"):
                self.add_error("purchase_category", "Purchase category is required for discounts.")

        return cleaned_data

class ArtworkUpdateForm(forms.ModelForm):
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Auction End Date",
    )

    class Meta:
        model = Artwork
        fields = [
            "product_name",
            "product_price",
            "product_image",
            "product_cat",
            "end_date",
            "length_in_centimeters",
            "width_in_centimeters",
            "foot",
            "inches",
        ]

    def clean_product_image(self):
        # Duplicate image detection logic
        uploaded_image = self.cleaned_data.get("product_image")
        if uploaded_image:
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.exclude(id=self.instance.id)

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(
                    Image.open(artwork.product_image.path)
                )
                if uploaded_image_hash == stored_image_hash:
                    raise forms.ValidationError(
                        "Duplicate image detected. This artwork has already been uploaded."
                    )
        return uploaded_image
