import datetime
from django import forms
from art.forms import FeedbackForm
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import Artwork, OrderModel, Catalogue, Bid, Notification, Query
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from PIL import Image
import imagehash
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
# Set up logging
logger = logging.getLogger(__name__)

class Index(View):
    def get(self, request):
        return render(request, 'dashboard/dashboard.html')

class ArtworkCreateView(LoginRequiredMixin, CreateView):
    model = Artwork
    fields = [
        "product_name", "product_price", "opening_bid", "product_cat", 
        "product_qty", "dimension_unit", "length_in_centimeters", "width_in_centimeters", 
        "foot", "inches", "product_image", "end_date"
    ]
    success_url = '/dashboard/product/'

    def get_form(self):
        form = super().get_form()
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        last_id = 1
        last_product = Artwork.objects.all().values('pk').last()
        if last_product:
            last_id = last_product['pk'] + 1

        try:
            cat = Catalogue.objects.get(pk=self.request.POST['product_cat']).cat_name[:3]
        except Catalogue.DoesNotExist:
            form.add_error('product_cat', 'Invalid category')
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.product_id = f'{cat}{last_id}'

        # Perform duplicate image detection before saving the object
        if self.request.FILES.get('product_image'):
            uploaded_image = self.request.FILES['product_image']
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.all()  # No need to exclude self.object since it's not created yet

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(Image.open(artwork.product_image.path))
                if uploaded_image_hash == stored_image_hash:
                    form.add_error('product_image', "Duplicate image detected. This artwork has already been uploaded.")
                    return self.form_invalid(form)

        # Now we can safely save the object
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ArtworkUpdateView(LoginRequiredMixin, UpdateView):
    model = Artwork
    fields = [
        "product_name", "product_price", "product_image", 
        "product_cat", "end_date", "length_in_centimeters", 
        "width_in_centimeters", "foot", "inches"
    ]
    template_name_suffix = '_update_form'
    success_url = '/dashboard/product/'

    def get_form(self):
        form = super().get_form()
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        # Duplicate image detection logic
        if self.request.FILES.get('product_image'):
            uploaded_image = self.request.FILES['product_image']
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.exclude(id=self.object.id)

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(Image.open(artwork.product_image.path))
                if uploaded_image_hash == stored_image_hash:
                    form.add_error('product_image', "Duplicate image detected. This artwork has already been uploaded.")
                    return self.form_invalid(form)

        return super().form_valid(form)

class BidCreateView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            bid_amt = float(request.POST.get("bid_amt", 0))
            product_id = request.POST.get("product")
            product_object = get_object_or_404(Artwork, pk=product_id)

            highest_bid = Bid.objects.filter(product=product_object).order_by("-bid_amt").first()

            # Case when there is no bid yet
            if highest_bid is None:
                min_bid = product_object.opening_bid
                if bid_amt < min_bid:
                    messages.error(request, "Your bid must be equal or greater than the opening bid amount.")
                    return redirect(request.META.get('HTTP_REFERER', 'art:artwork_detail'))

            # Case when there is already a highest bid
            else:
                min_bid = highest_bid.bid_amt
                if bid_amt <= min_bid:
                    messages.error(request, "Your bid must be higher than the current highest bid.")
                    return redirect(request.META.get('HTTP_REFERER', 'art:artwork_detail'))

            # If all checks pass, create the bid
            Bid.objects.create(user=request.user, bid_amt=bid_amt, product=product_object)

            # Notify previous bidders
            previous_bidders = Bid.objects.filter(product=product_object).exclude(user=request.user).values_list('user', flat=True).distinct()
            for bidder in previous_bidders:
                Notification.objects.create(
                    user_id=bidder,
                    product=product_object,
                    message=f"A new bid has been placed on {product_object.product_name}"
                )

            messages.success(request, "Your bid has been placed successfully.")
            return redirect(request.META.get('HTTP_REFERER', 'art:artwork_detail'))

        except Exception as e:
            logger.error(f'Error placing bid: {e}')
            messages.error(request, "An error occurred while placing your bid. Please try again later.")
            return redirect(request.META.get('HTTP_REFERER', 'art:artwork_detail'))
        
from django.utils.timezone import now
# Check auction status and notify the highest bidder
def check_auction_status():
    products = Artwork.objects.filter(end_date__lte=now(), status='active')
    for product in products:
        highest_bid = product.bids.order_by('-bid_amt').first()
        if highest_bid:
            # Notify the highest bidder via email
            send_mail(
                subject=f"You've won the auction for '{product.product_name}'!",
                message=(
                    f"Congratulations! You've won the auction for '{product.product_name}' at ₹{highest_bid.bid_amt}.\n\n"
                    f"Click here to confirm your purchase within 12 hours:\n"
                    f"http://127.0.0.1:8000/confirm_purchase/{product.id}/?response=yes\n\n"
                    f"Click here if you do not want to purchase:\n"
                    f"http://127.0.0.1:8000/confirm_purchase/{product.id}/?response=no\n\n"
                    f"You have 12 hours to respond."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[highest_bid.user.email],
            )
            product.status = 'waiting_for_response'
            product.response_deadline = now() + datetime.timedelta(hours=12)
        else:
            product.status = 'unsold'
        product.save()

# Handle buyer's response
def confirm_purchase(request, artwork_id):
    response = request.GET.get('response')
    product = get_object_or_404(Artwork, pk=artwork_id)

    if response == 'yes':
        product.status = 'closed'
        product.buyer_response = 'yes'
        product.is_sold = True
        product.save()
        return redirect('art:order_form')  # Redirect to checkout
    elif response == 'no':
        product.status = 'unsold'
        product.buyer_response = 'no'
        product.save()
        return render(request, 'art/unsold.html', {'message': 'The artwork has been marked as unsold.'})
    else:
        return render(request, 'dashboard/404.html', {'message': 'Invalid response.'})

# Move expired artworks to unsold
def check_expired_responses():
    expired_artworks = Artwork.objects.filter(
        response_deadline__lte=now(),
        status='waiting_for_response',
        buyer_response='no_response'
    )
    for product in expired_artworks:
        product.status = 'unsold'
        product.save()

def latest_bid(request, pk):
    try:
        artwork = get_object_or_404(Artwork, pk=pk)
        last_bid = Bid.objects.filter(product=artwork).order_by('-bid_amt').first()
        total_bids = Bid.objects.filter(product=artwork).count()
        data = {
            'last_bid': last_bid.bid_amt if last_bid else artwork.opening_bid,
            'total_bids': total_bids
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f'Error fetching latest bid: {e}')
        return JsonResponse({'success': False, 'message': f"Error fetching latest bid. Error: {e}"})

class ArtworkListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = 'dashboard/artwork_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        filter_type = self.request.GET.get('filter', 'all')

        if filter_type == 'new':
            cutoff_date = timezone.now() - timezone.timedelta(days=3)
            queryset = Artwork.objects.filter(user=self.request.user, created_at__gte=cutoff_date)
        elif filter_type == 'old':
            cutoff_date = timezone.now() - timezone.timedelta(days=3)
            queryset = Artwork.objects.filter(user=self.request.user, created_at__lt=cutoff_date)
        elif filter_type == 'sold':
            queryset = Artwork.objects.filter(user=self.request.user, is_sold=True)
        else:
            queryset = Artwork.objects.filter(user=self.request.user)

        print("Filter Type:", filter_type)
        print("Queryset Count:", queryset.count())  # Debug: Check queryset count

        return queryset
    
    # def sold_artworks(request):
    #     sold_artworks = Artwork.objects.filter(is_sold=True)
    #     context = {
    #         'sold_artworks': sold_artworks
    #     }
    #     return render(request, 'artwork_list.html', context)
class BidListView(LoginRequiredMixin, ListView):
    model = Bid
    template_name = 'dashboard/bids_list.html'
    context_object_name = 'bids'
    ordering = ['-bid_amt']  # Default ordering by highest bid

    def get_queryset(self):
        queryset = super().get_queryset()

        # Handle sorting based on URL parameter 'filter'
        filter_param = self.request.GET.get('filter')
        if filter_param == 'asc':
            queryset = queryset.order_by('bid_amt')  # Ascending order by bid amount
        elif filter_param == 'desc':
            queryset = queryset.order_by('-bid_amt')  # Descending order by bid amount
        else:
            queryset = queryset.order_by('-bid_amt')  # Default to descending if no filter param

        return queryset

class ArtworkUpdateView(LoginRequiredMixin, UpdateView):
    model = Artwork
    fields = [
        "product_name", "product_price", "product_image", 
        "product_cat", "end_date", "length_in_centimeters", 
        "width_in_centimeters", "foot", "inches"
    ]
    template_name_suffix = '_update_form'
    success_url = '/dashboard/product/'

    def get_form(self):
        form = super().get_form()
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

class ArtworkDeleteView(LoginRequiredMixin, DeleteView):
    model = Artwork
    success_url = reverse_lazy('dashboard:product_list')

class OrderListView(LoginRequiredMixin, ListView):
    model = OrderModel
    template_name = 'dashboard/ordermodel_list.html'

    def get_queryset(self):
        queryset = OrderModel.objects.all()
        
        # Filter orders based on user group
        if self.request.user.groups.filter(name='SellerGroup').exists():
            queryset = queryset.filter(product__user=self.request.user)
        else:
            queryset = queryset.filter(user=self.request.user)
        
        # Handle sorting based on URL parameter 'filter'
        filter_param = self.request.GET.get('filter')
        if filter_param == 'asc':
            queryset = queryset.order_by('order_date')
        elif filter_param == 'desc':
            queryset = queryset.order_by('-order_date')

        return queryset

class ArtworkDetailView(LoginRequiredMixin, DetailView):
    model = Artwork
    template_name = 'art/artwork_detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artwork = self.get_object()
        last_bid = Bid.objects.filter(product=artwork).order_by('-bid_amt').first()
        total_bids = Bid.objects.filter(product=artwork).count()
        context['last_bid'] = last_bid.bid_amt if last_bid else artwork.opening_bid
        context['total_bids'] = total_bids
        context['foot'] = artwork.foot
        context['inches'] = artwork.inches
        return context

@login_required
def fetch_notifications(request):
    try:
        notifications = Notification.objects.filter(user=request.user, read=False)
        notifications_data = [{
            'id': n.id,
            'message': n.message,
            'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'product_id': n.product.id if n.product else None  # Include product ID
        } for n in notifications]

        # Mark notifications as read
        notifications.update(read=True, read_at=timezone.now())

        return JsonResponse({'notifications': notifications_data})
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def mark_notification_as_read(request, notification_id):
    if request.method == 'POST':
        try:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


from django.urls import reverse_lazy
class SubmitQueryView(FormView):
    template_name = 'art/contact.html'
    success_url = reverse_lazy('art:contact')

    def post(self, request, *args, **kwargs):
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        query = request.POST.get('query')

        if full_name and email and query:
            query = Query(
                full_name=full_name,
                email=email,
                query=query
            )
            query.save()
            messages.success(request, 'Your query has been submitted successfully.')
            return redirect('art:contact')
        else:
            messages.error(request, 'Please fill out all fields.')
            return redirect('art:contact')
        
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your feedback has been submitted.')
            return redirect('art:callback')  # Redirect to a thank you page or callback page
    else:
        form = FeedbackForm()
    
    return render(request, 'art/index.html', {'form': form})