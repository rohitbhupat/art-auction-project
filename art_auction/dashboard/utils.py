from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from dashboard.models import Artwork

def send_highest_bid_email():
    # Get all artworks whose auction has ended and haven't been processed
    products = Artwork.objects.filter(end_date__lt=timezone.now(), highest_bidder__isnull=True)

    for product in products:
        # Get the highest bid for each artwork
        highest_bid = product.bids.order_by('-bid_amt').first()

        if highest_bid:
            # Set the highest bid details on the artwork
            product.highest_bid = highest_bid.bid_amt
            product.highest_bidder = highest_bid.user
            product.save()

            # Send email to the highest bidder
            send_mail(
                f"Congratulations! You've won the auction for {product.title}",
                f"Dear {highest_bid.user.username},\n\nYou have won the auction for '{product.title}' with a bid of {highest_bid.bid_amt}.",
                settings.DEFAULT_FROM_EMAIL,
                [highest_bid.user.email],
            )

            # Optionally, send an email to the seller (if applicable)
            if product.seller:  # Assuming artwork has a seller field
                send_mail(
                    f"The auction for {product.title} has ended",
                    f"Dear {product.seller.username},\n\nThe auction for your artwork '{product.title}' has ended. The highest bid was {highest_bid.bid_amt}.",
                    settings.DEFAULT_FROM_EMAIL,
                    [product.seller.email],
                )
            print(f"Email sent for artwork {product.title} with bid {highest_bid.bid_amt}")
        else:
            print(f"No bids placed for artwork {product.title}")
