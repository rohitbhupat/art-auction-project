from django.core.management.base import BaseCommand
from django.utils.timezone import now
from dashboard.models import Artwork
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.db.models.functions import TruncDate

class Command(BaseCommand):
    help = 'Send email to the highest bidder of expired auctions'

    def handle(self, *args, **kwargs):
        # Get all active artworks whose auction has already ended
        expired_auctions = Artwork.objects.annotate(truncated_end_date=TruncDate('end_date')).filter(
            truncated_end_date__lte=now().date(),
            status='active'
        )
        
        for product in expired_auctions:
            print(f"Artwork: {product.product_name}, End Date: {product.end_date}, Status: {product.status}")
            # Get the highest bid
            highest_bid = product.bids.order_by('-bid_amt').first()
            
            if highest_bid:
                # Send email to the highest bidder
                send_mail(
                    subject=f"Congratulations! You've won the auction for '{product.product_name}'!",
                    message=(
                        f"Dear {highest_bid.user.username},\n\n"
                        f"You've won the auction for '{product.product_name}' with a bid of ₹{highest_bid.bid_amt}.\n\n"
                        f"Please confirm your purchase within 12 hours using the following link:\n"
                        f"http://127.0.0.1:8000/confirm_purchase/{product.id}/?response=yes\n\n"
                        f"Decline by clicking here:\n"
                        f"http://127.0.0.1:8000/confirm_purchase/{product.id}/?response=no\n\n"
                        f"If no response is received within 12 hours, the artwork will be marked as unsold."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[highest_bid.user.email],
                )
                # Update the artwork status
                product.status = 'waiting_for_response'
                product.response_deadline = now() + timedelta(hours=12)
            else:
                # If no bids, mark artwork as unsold
                product.status = 'unsold'
            
            # Save the changes to the artwork
            product.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully sent email notifications to highest bidders'))
