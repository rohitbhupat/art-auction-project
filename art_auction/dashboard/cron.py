import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from dashboard.models import Artwork
from django_cron import CronJobBase, Schedule

logger = logging.getLogger(__name__)

class AuctionCronJob(CronJobBase):
    RUN_EVERY_MINS = 15  # Run every 15 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dashboard.auction_cron_job'  # A unique code

    def do(self):
        try:
            active_products = Artwork.objects.filter(end_date__lte=now().date(), status='active')
            logger.info(f"Found {active_products.count()} active products to process.")

            for product in active_products:
                highest_bid = product.bids.order_by('-bid_amt').first()  # Update if 'bids' is incorrect
                if highest_bid:
                    try:
                        logger.info(f"Sending email to {highest_bid.user.email} for product {product.product_name}")
                        send_mail(
                            subject=f"You've won the auction for '{product.product_name}'!",
                            message=(
                                f"Confirm purchase within 12 hours: "
                                f"http://127.0.0.1:8000/confirm_purchase/{product.id}/?response=yes\n"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[highest_bid.user.email],
                        )
                        product.status = 'waiting_for_response'
                        product.response_deadline = now() + timedelta(hours=12)
                    except Exception as e:
                        logger.error(f"Failed to send email for {product.product_name}: {e}")
                else:
                    logger.info(f"No bids found for product {product.product_name}. Marking as unsold.")
                    product.status = 'unsold'
                product.save()

            # Handle expired responses
            expired_products = Artwork.objects.filter(status='waiting_for_response', response_deadline__lte=now())
            for expired_product in expired_products:
                if expired_product.buyer_response == 'no_response':
                    expired_product.status = 'unsold'
                expired_product.save()

        except Exception as e:
            logger.error(f"AuctionCronJob failed: {e}")
