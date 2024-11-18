from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from dashboard.models import Artwork
from django.conf import settings

class Command(BaseCommand):
    help = 'Send highest bid email after auction ends'

    def handle(self, *args, **kwargs):
        # Get all active artworks whose auction has ended
        products = Artwork.objects.filter(end_date__lt=now(), status='active')

        for product in products:
            # Get the highest bid for each artwork
            highest_bid = product.bids.order_by('-bid_amt').first()

            if highest_bid:
                # Send email to the highest bidder
                send_mail(
                    subject=f"You've won the auction for '{product.product_name}'!",
                    message=(
                        f"Congratulations! You've won the auction for '{product.product_name}' at ₹{highest_bid.bid_amt}.\n\n"
                        f"Confirm your purchase within 12 hours by clicking here:\n"
                        f"http://yourdomain.com/confirm_purchase/{product.id}/?response=yes\n\n"
                        f"Decline by clicking here:\n"
                        f"http://yourdomain.com/confirm_purchase/{product.id}/?response=no\n\n"
                        f"If no response is received within 12 hours, the artwork will be moved to unsold items."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[highest_bid.user.email],
                )
                product.status = 'waiting_for_response'
                product.response_deadline = now() + timedelta(hours=12)  # Set 12-hour deadline
            else:
                product.status = 'unsold'  # No bids

            product.save()

        # Handle expired response deadlines
        expired_products = Artwork.objects.filter(status='waiting_for_response', response_deadline__lte=now())
        for expired_product in expired_products:
            if expired_product.buyer_response == 'no_response':
                expired_product.status = 'unsold'
            expired_product.save()
