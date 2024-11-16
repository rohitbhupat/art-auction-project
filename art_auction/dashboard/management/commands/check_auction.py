from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from dashboard.models import Artwork
from django.conf import settings

class Command(BaseCommand):
    help = 'Check auction status and notify highest bidders'

    def handle(self, *args, **kwargs):
        products = Artwork.objects.filter(end_date__lte=now(), status='active')

        for product in products:
            highest_bid = product.bids.order_by('-bid_amt').first()
            if highest_bid:
                send_mail(
                    subject=f"You've won the auction for '{product.product_name}'!",
                    message=(
                        f"Congratulations! You've won the auction for '{product.product_name}' at ₹{highest_bid.bid_amt}.\n\n"
                        f"Click on the following link to confirm your purchase within 12 hours:\n"
                        f"http://yourdomain.com/confirm_purchase/{product.id}/?response=yes\n\n"
                        f"If you do not want to proceed, click here:\n"
                        f"http://yourdomain.com/confirm_purchase/{product.id}/?response=no\n\n"
                        f"You have 12 hours to respond."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[highest_bid.user.email],
                )
                product.status = 'waiting_for_response'
            else:
                product.status = 'unsold'

            product.save()
