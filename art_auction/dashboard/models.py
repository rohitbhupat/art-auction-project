from datetime import datetime, time
from time import localtime
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
import imagehash
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.timezone import make_aware
import pytz

class Catalogue(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name


class Artwork(models.Model):

    SALE_TYPE_CHOICES = [
        ("discount", "Discount"),
        ("auction", "Auction"),
    ]
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES)  # sale_type only
    product_id = models.CharField(max_length=255, default="")
    product_name = models.CharField(max_length=255, blank=False)
    product_price = models.IntegerField(default=0)
    opening_bid = models.IntegerField(default=0, null=True, blank=True)
    product_cat = models.ForeignKey("Catalogue", on_delete=models.CASCADE, null=True, blank=True)
    product_qty = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to="arts/")
    dimension_unit = models.CharField(max_length=2, choices=[("cm", "Centimeters"), ("ft", "Feet")])
    length_in_centimeters = models.FloatField(default=0.0, blank=True, null=True)
    width_in_centimeters = models.FloatField(default=0.0, blank=True, null=True)
    foot = models.FloatField(default=0, blank=True, null=True)
    inches = models.FloatField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50,
        choices=[("active", "Active"), ("closed", "Closed"), ("waiting_for_response", "Waiting for Response"), ("unsold", "Unsold")],
        default="active",
    )
    response_deadline = models.DateTimeField(blank=True, null=True, db_index=True)
    buyer_response = models.CharField(max_length=11, choices=[("yes", "Yes"), ("no", "No"), ("no_response", "No Response")], default="no_response")
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def get_discounted_price(self):
        """Calculate 30% discounted price."""
        return self.product_price * 0.7

    def save(self, *args, **kwargs):
        # Duplicate image detection logic
        if self.product_image:
            existing_images = Artwork.objects.exclude(
                id=self.id
            )  # Exclude self during update
            uploaded_image_hash = imagehash.phash(Image.open(self.product_image))
        
        if self.end_date:
            # Ensure end_date is always set to 12:00 a.m.
            self.end_date = make_aware(datetime.combine(self.end_date, time.min))
            for artwork in existing_images:
                stored_image_hash = imagehash.phash(
                    Image.open(artwork.product_image.path)
                )
                if uploaded_image_hash == stored_image_hash:
                    raise ValidationError(
                        "Duplicate image detected. This artwork is already an NFT and cannot be uploaded again."
                    )
        # Fix for 'created_at' - Ensure it's a datetime object
        if not self.id:  # Only set `created_at` when it's a new object
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        super(Artwork, self).clean()
        
        if self.sale_type == 'discount':
            # Ignore product_cat, opening_bid, and end_date for discount sale type
            self.product_cat = None
            self.opening_bid = None
            self.end_date = None
            
        if self.discounted_price and self.discounted_price >= self.product_price:
            raise ValidationError({"discounted_price": "Discounted price must be less than the product price."})
        
        if self.end_date:
            # Normalize end_date to 12:00 a.m. IST
            local_tz = pytz.timezone(settings.TIME_ZONE)  # Use pytz to get the timezone
            self.end_date = make_aware(datetime.combine(self.end_date, time.min), local_tz)
        
        elif self.sale_type == 'auction':
            if not self.product_cat:
                raise ValidationError({"product_cat": "Product category is required for bidding."})
            if not self.opening_bid:
                raise ValidationError({"opening_bid": "Opening bid is required for bidding."})
            if not self.end_date:
                raise ValidationError({"end_date": "End date is required for bidding."})
    def __str__(self):
        return self.product_name

    def get_last_bid(self):
        last_bid = self.bids.order_by("-bid_amt").first()
        return last_bid.bid_amt if last_bid else self.opening_bid

    def get_total_bids(self):
        return self.bids.count()

    def mark_as_sold(self):
        self.is_sold = True
        self.save()

class OrderModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    order_qty = models.IntegerField(default=0, null=False)
    delivery_at = models.TextField(default=" ", null=False)
    order_price = models.FloatField(default=0, null=False)

    def __str__(self):
        return f"order of {self.product} by {self.user}"


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateField(auto_now_add=True)
    bid_amt = models.IntegerField(default=1)

    def __str__(self):
        return f"bid of {self.product} on {self.bid_date}"


class Payment(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        _("Payment Status"), max_length=254, default="Pending", blank=False, null=False
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.provider_order_id}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Artwork, on_delete=models.CASCADE, null=True, blank=True
    )  # Adjust as necessary
    message = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Query(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    query = models.TextField()
    category = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.category}"


from django.db import models


class Feedback(models.Model):
    RATING_CHOICES = [
        ("Poor", "Poor"),
        ("Fair", "Fair"),
        ("Good", "Good"),
        ("Very Good", "Very Good"),
        ("Excellent", "Excellent"),
    ]

    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True, null=True)
    sentiment = models.CharField(
        max_length=10,
        choices=[
            ("positive", "Positive"),
            ("negative", "Negative"),
            ("neutral", "Neutral"),
        ],
        blank=True,
        null=True,
    )  # Added sentiment field
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} - {self.feedback_text[:50]}..."


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50)  # e.g., 'view', 'like', 'bid'
    timestamp = models.DateTimeField(auto_now_add=True)
