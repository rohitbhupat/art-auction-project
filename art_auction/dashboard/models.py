from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Catalogue(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name

class Artwork(models.Model):
    product_id = models.CharField(max_length=255, default="")
    product_name = models.CharField(max_length=255, default="", blank=False, null=False)
    product_price = models.IntegerField(default=0, null=False)
    opening_bid = models.IntegerField(default=0)
    product_cat = models.ForeignKey('Catalogue', on_delete=models.CASCADE)
    product_qty = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='arts/')
    dimension_unit = models.CharField(max_length=2, choices=[('cm', 'Centimeters'), ('ft', 'Feet')])
    length_in_centimeters = models.FloatField(default=0.0, blank=True, null=True)
    width_in_centimeters = models.FloatField(default=0.0, blank=True, null=True)
    foot = models.FloatField(default=0, blank=True, null=True)
    inches = models.FloatField(default=0, blank=True, null=True)
    end_date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_sold = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

    def __str__(self):
        return self.product_name

    def get_last_bid(self):
        last_bid = self.bid_set.order_by('-bid_amt').first()
        return last_bid.bid_amt if last_bid else self.opening_bid

    def get_total_bids(self):
        return self.bid_set.count()

class OrderModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    order_qty = models.IntegerField(default=0, null=False)
    delivery_at = models.TextField(default=" ", null=False)
    order_price = models.FloatField(default=0, null=False)

    def __str__(self):
        return f'order of {self.product} by {self.user}'

class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    bid_date = models.DateField(auto_now_add=True)
    bid_amt = models.IntegerField(default=1)

    def __str__(self):
        return f'bid of {self.product} on {self.bid_date}'

class Payment(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(_("Payment Status"), max_length=254, default='Pending', blank=False, null=False)
    provider_order_id = models.CharField(_("Order ID"), max_length=40, null=False, blank=False)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=False, blank=False)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=False, blank=False)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.provider_order_id}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE, null=True, blank=True)  # Adjust as necessary
    message = models.TextField()
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

