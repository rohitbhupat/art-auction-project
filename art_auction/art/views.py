from django.conf import settings
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth.models import Group
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from art.forms import (
    UserRegistrationForm,
    LoginForm,
    SellerInfoForm,
    UserForm,
    SellerForm,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import razorpay
from django.http import JsonResponse
import re
from dashboard.models import Payment, Artwork, OrderModel, Bid, Catalogue
from django.views.decorators.csrf import csrf_exempt
import json
from dashboard.constants import PaymentStatus
import datetime
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

# Import the SellerInfo model
from art.models import SellerInfo, UserInfo
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone
from datetime import date, timedelta
class index(View):
    def get(self, request):
        filter_param = request.GET.get("filter", "")
        current_date = date.today()  # Use date.today() to get the current date without time

        if filter_param == "old":
            # Define the threshold for old artworks (e.g., 1 day old)
            old_threshold_date = current_date - timedelta(days=1)
            product_object_list = Artwork.objects.filter(
                created_at__lt=old_threshold_date,
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="bidding"  # Ensure only bidding artworks are fetched
            )
        elif filter_param == "new":
            # Define the threshold for new artworks (e.g., created in the last 1 day)
            new_threshold_date = current_date - timedelta(days=1)
            product_object_list = Artwork.objects.filter(
                created_at__gte=new_threshold_date,
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="bidding"  # Ensure only bidding artworks are fetched
            )
        else:
            # Default view shows artworks ending today or later
            product_object_list = Artwork.objects.filter(
                end_date__gte=current_date,
                product_qty__gt=0,
                is_sold=False,  # Ensure only unsold artworks are considered
                sale_type="bidding"  # Ensure only bidding artworks are fetched
            )

        # Debugging: Print out the filtered products to verify the logic
        for product in product_object_list:
            print(
                f"Product ID: {product.product_id}, Created Date: {product.created_at}, End Date: {product.end_date}, Sale Type: {product.sale_type}"
            )

        return render(
            request,
            "art/index.html",
            {
                "product_object_list": product_object_list,
                "catalogue_list": Catalogue.objects.all(),  # Adjust as per your context
                "current_date": current_date,
            },
        )


@login_required
def profile_settings(request):
    is_seller = request.user.groups.filter(name="SellerGroup").exists()
    user_info, created = UserInfo.objects.get_or_create(user=request.user)

    try:
        seller_info = request.user.sellerinfo
    except SellerInfo.DoesNotExist:
        seller_info = None

    # Forms
    user_form = UserForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)  # Password change form
    seller_form = SellerForm(instance=seller_info) if is_seller else None
    initial_data = {"phone_number": user_info.phone_number}

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        seller_form = (
            SellerForm(request.POST, instance=seller_info) if is_seller else None
        )

        # Validate forms
        if user_form.is_valid() and (not is_seller or seller_form.is_valid()):
            user = user_form.save()
            user_info.phone_number = request.POST.get("phone_number")
            user_info.save()

            if is_seller:
                seller_info = seller_form.save(commit=False)
                seller_info.user = user
                seller_info.save()

            # Handle password change
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)

            messages.success(request, "Your profile has been updated successfully.")
            return redirect("art:profile_settings")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(
        request,
        "art/profile_settings.html",
        {
            "userForm": user_form,
            "sellerForm": seller_form,
            "passwordForm": password_form,
            "is_seller": is_seller,
            "phone_number": initial_data["phone_number"],
        },
    )


class CatListView(View):
    def catalog_products(request, id):
        catalog = get_object_or_404(Catalogue, id=id)
        filter_option = request.GET.get("filter")

        if filter_option == "asc":
            products = Artwork.objects.filter(
                product_cat=catalog, product_qty__gt=0
            ).order_by("end_date")
        elif filter_option == "desc":
            products = Artwork.objects.filter(
                product_cat=catalog, product_qty__gt=0
            ).order_by("-end_date")
        else:
            products = Artwork.objects.filter(product_cat=catalog, product_qty__gt=0)

        return render(
            request,
            "art/catalog_products.html",
            {
                "catalog": catalog,
                "product_object_list": products,
                "catalogue_list": Catalogue.objects.all(),
            },
        )


def register_user(request):
    if request.user.is_authenticated:
        return redirect("art:index")
    else:
        if request.method == "POST":
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    login(request, user)
                    messages.success(request, "Registration successful.")
                    return redirect("art:index")
                except IntegrityError as e:
                    messages.error(request, f"An error occurred: {str(e)}")
            else:
                messages.error(request, form.errors)

    form = UserRegistrationForm()
    return render(
        request=request,
        template_name="art/signup.html",
        context={"register_form": form},
    )


class RegisterSeller(View):
    def post(self, request):
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        phone_number = request.POST["phone_number"]
        business_name = request.POST["business_name"]

        userform = UserRegistrationForm(
            {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "password1": password1,
                "password2": password2,
            }
        )

        if userform.is_valid():
            user = userform.save()
            sellerGroup = Group.objects.get(name="SellerGroup")
            user.groups.add(sellerGroup)

            # Check if SellerInfo already exists for the user
            try:
                seller_info = user.sellerinfo
            except SellerInfo.DoesNotExist:
                seller_info = None

            if seller_info:
                # Update existing SellerInfo
                sellerForm = SellerInfoForm(request.POST, instance=seller_info)
            else:
                # Create new SellerInfo
                sellerForm = SellerInfoForm(request.POST)

            if sellerForm.is_valid():
                seller_info = sellerForm.save(commit=False)
                seller_info.user = user
                seller_info.save()
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect("art:index")
            else:
                messages.error(request, sellerForm.errors)

        messages.error(request, userform.errors)
        userform = UserRegistrationForm()
        sellerForm = SellerInfoForm()
        return render(
            request=request,
            template_name="art/registerseller.html",
            context={"userform": userform, "sellerForm": sellerForm},
        )

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:dashboard")
        userform = UserRegistrationForm()
        sellerForm = SellerInfoForm()
        return render(
            request=request,
            template_name="art/registerseller.html",
            context={"userform": userform, "sellerForm": sellerForm},
        )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("art:index")

    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            upass = form.cleaned_data["password"]
            user = authenticate(request, username=uname, password=upass)
            if user is not None:
                login(request, user)

                # Check if the user is part of the SellerGroup
                if user.groups.filter(name="SellerGroup").exists():
                    # Ensure seller information exists
                    SellerInfo.objects.get_or_create(user=user)

                    # Fetch related data for the seller
                    total_order = OrderModel.objects.filter(product__user=user).count()
                    total_product = Artwork.objects.filter(user=user).count()
                    return render(
                        request,
                        "art/index.html",
                        context={
                            "is_Seller": True,
                            "total_order": total_order,
                            "total_product": total_product,
                        },
                    )

                # Non-seller user
                return render(request, "art/index.html", context={"is_Seller": False})

            # Authentication failed
            messages.error(request, "Please correct the errors below.")
        else:
            messages.error(request, "Your username or password is incorrect.")

    else:
        form = LoginForm()

    return render(request, "art/signin.html", context={"login_form": form})


class Profile(LoginRequiredMixin, TemplateView):
    template_name = "social-media/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = PostObject()
        context["object_list"] = obj.get_all_posts().order_by("-created_on")
        context["business_list"] = Business.objects.all().filter(
            created_by=self.request.user
        )
        if UserProfile.objects.filter(user=self.request.user).exists():
            context["profileObj"] = UserProfile.objects.get(user=self.request.user)
            if self.request.user.userprofile.is_verified == False:
                context["is_profile_not_complete"] = True
                context["profile_form"] = UserProfileForm()
        else:
            UserProfile(user=self.request.user, dob=None, phone_number=0).save()

        return context


def logout_view(request):
    logout(request)
    return redirect("art:index")


class ArtworkDetailView(DetailView):
    model = Artwork
    template_name = "art/artwork_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_bid"] = Bid.objects.filter(product=self.kwargs.get("pk")).last()
        context["total_bid"] = Bid.objects.filter(product=self.kwargs.get("pk")).count()
        return context


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = Artwork.objects.get(pk=self.kwargs.get("pk"))
        product_object.product_qty = 0
        product_object.save()
        last_bid = Bid.objects.filter(product=self.kwargs.get("pk")).last()
        return render(
            request=request,
            template_name="art/order_form.html",
            context={"product": product_object, "last_bid": last_bid},
        )

    def post(self, request, *args, **kwargs):
        product = Artwork.objects.get(pk=request.POST["product"])
        product_price = request.POST["product_price"]
        product_qty = request.POST["product_qty"]
        delivery_at = request.POST["delivery_at"]
        order = OrderModel.objects.create(
            product=product,
            order_qty=product_qty,
            order_price=product_price,
            delivery_at=delivery_at,
            user=self.request.user,
        )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create(
            {
                "amount": (int(product_price) * 100) * int(product_qty),
                "currency": "INR",
                "payment_capture": "1",
            }
        )
        order = Payment.objects.create(
            order=order,
            status=PaymentStatus.SUCCESS,
            provider_order_id=razorpay_order["id"],
        )

        # Ensure product quantity is set to zero to mark as sold
        product.product_qty = 0
        product.save()

        return render(
            request,
            "art/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )


@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        logger.debug(f"Received POST data: {request.POST}")  # Log the POST data

        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")
            order = Payment.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id
            order.payment_method = request.POST.get("method")  # Capture payment method
            order.save()

            logger.debug(
                f"Payment Method: {order.payment_method}"
            )  # Log the payment method

            if verify_signature(request.POST):
                order.status = PaymentStatus.SUCCESS
            else:
                order.status = PaymentStatus.FAILURE
            order.save()

            return render(
                request, "art/callback.html", context={"status": "Payment done"}
            )
        except Payment.DoesNotExist:
            logger.error(
                f"Payment with provider_order_id {provider_order_id} does not exist."
            )
            return render(
                request,
                "art/callback.html",
                context={"status": "Payment failed", "error": "Invalid order ID"},
            )
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return render(
                request,
                "art/callback.html",
                context={"status": "Payment failed", "error": str(e)},
            )
    else:
        return render(
            request, "art/callback.html", context={"status": "Payment failed"}
        )


class SaleOrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = Artwork.objects.get(pk=self.kwargs.get("pk"))

        # Check if the user has purchased this product before
        previous_order = OrderModel.objects.filter(
            user=request.user, product=product_object
        ).exists()

        # Determine the price based on purchase history
        if not previous_order:
            price = product_object.product_price * 0.7  # 30% discount
            is_first_purchase = True
        else:
            price = product_object.product_price
            is_first_purchase = False

        return render(
            request,
            "art/sale-order-form.html",
            {
                "product": product_object,
                "price": price,
                "is_first_purchase": is_first_purchase,
            },
        )

    def post(self, request, *args, **kwargs):
        product = Artwork.objects.get(pk=request.POST["product"])
        product_price = request.POST["product_price"]
        product_qty = request.POST["product_qty"]
        delivery_at = request.POST["delivery_at"]

        # Create the order
        order = OrderModel.objects.create(
            product=product,
            order_qty=product_qty,
            order_price=product_price,
            delivery_at=delivery_at,
            user=request.user,
        )

        # Update product quantity
        product.product_qty -= int(product_qty)
        product.save()

        # Process payment
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create(
            {
                "amount": int(product_price) * int(product_qty) * 100,
                "currency": "INR",
                "payment_capture": "1",
            }
        )
        Payment.objects.create(
            order=order,
            status=PaymentStatus.SUCCESS,
            provider_order_id=razorpay_order["id"],
        )

        return render(
            request,
            "art/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
            },
        )

class ArView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_object = Artwork.objects.get(pk=self.kwargs.get("id"))
        return render(
            request, "art/ArView.html", context={"image": product_object.product_image}
        )


class About(TemplateView):
    template_name = "art/about.html"


class Contact(TemplateView):
    template_name = "art/contact.html"


class FAQs(TemplateView):
    template_name = "art/faq.html"


class UnsoldListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "art/unsold.html"
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Artwork.objects.filter(
            end_date__lt=timezone.now(), product_qty__gt=0
        )

        # Handle sorting based on URL parameter 'filter'
        filter_param = self.request.GET.get("filter", None)
        if filter_param == "asc":
            queryset = queryset.order_by("end_date")
        elif filter_param == "desc":
            queryset = queryset.order_by("-end_date")

        return queryset

class ArtworkSaleDetailView(DetailView):
    model = Artwork
    template_name = "art/artwork-sale_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Check if the user has purchased this product before
        if self.request.user.is_authenticated:
            previous_order = OrderModel.objects.filter(user=self.request.user, product=product).exists()
        else:
            previous_order = False

        if previous_order:
            # Original price for subsequent purchases
            context["price"] = product.product_price
            context["is_first_purchase"] = False
        else:
            # Discounted price for the first purchase
            context["price"] = product.product_price * 0.7
            context["is_first_purchase"] = True

        # Pass recommended artworks
        context["recommended_artworks"] = Artwork.objects.exclude(pk=product.pk)[:4]
        return context

class ArtworkSaleListView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "art/artwork_sale.html"
    context_object_name = "object_list"

    def get_queryset(self):
        # Filter artworks for sale only (exclude bidding)
        queryset = Artwork.objects.filter(
            product_qty__gt=0,
            is_sold=False,
            sale_type="discount",  # Ensure only artworks with sale_type "sale" are displayed
        )

        if self.request.user.is_authenticated:
            # Add discounted price for first-time buyers
            for artwork in queryset:
                previous_order = OrderModel.objects.filter(user=self.request.user, product=artwork).exists()
                if not previous_order:
                    artwork.discounted_price = artwork.product_price * 0.7  # Apply 30% discount
                else:
                    artwork.discounted_price = artwork.product_price

        return queryset