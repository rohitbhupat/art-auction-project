from django.conf import settings
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth.models import Group
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from art.forms import UserRegistrationForm, LoginForm, SellerInfoForm
from django.contrib.auth.forms import AuthenticationForm
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
from dashboard.models import Catalogue


class index(View):
    def get(self, request):

        # return render(request,'art/index.html',{'news':self.get_news,'public_post':self.post_obj.get_all_posts().order_by('-created_on')[:5]})
        return render(
            request,
            "art/index.html",
            {
                "product_object_list": Artwork.objects.filter(
                    end_date__gte=datetime.date.today(),
                    product_qty__gt = 0
                ),
                "catalogue_list": Catalogue.objects.all(),
            },
        )
# class IndexView(TemplateView):
#     template_name = 'dashboard/index.html'
    
class CatListView(View):
    def catalog_products(request, id):
        catalog = get_object_or_404(Catalogue, id=id)
        products = Artwork.objects.filter(product_cat=catalog ,  product_qty__gt = 0)
        return render(
            request, 
            "art/catalog_products.html", 
            {
                "catalog": catalog,
                "product_object_list": products,  # Update context variable name
                "catalogue_list": Catalogue.objects.all()  # Include catalogue list for navbar
            }
        )



def register_user(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    else:
        if request.method == "POST":
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect("art:index")

            form.clean_password2()
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
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        phone_number = request.POST["phone_number"]
        business_name = request.POST["business_name"]
        userform = UserRegistrationForm({
            "first_name":first_name,
            "last_name":last_name,
            "username":username,
            "email":email,
            "password1":password1,
            "password2":password2
            })
      
        if userform.is_valid():
            user = userform.save()
            sellerGroup = Group.objects.get(name = 'SellerGroup')
            user.groups.add(sellerGroup)
            sellerForm = SellerInfoForm({
            "user":user,
            "phone_number":phone_number,
            "business_name":business_name
            })
            if sellerForm.is_valid():
                # sellerForm.user = user
                sellerForm.save()
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect("art:index")
            messages.error(request, sellerForm.errors)

        messages.error(request, userform.errors)
        userform = UserRegistrationForm()
        sellerForm = SellerInfoForm()
        return render(request=request, template_name="art/registerseller.html", context={"userform": userform,"sellerForm":sellerForm})
        

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:dashboard")
        userform = UserRegistrationForm()
        sellerForm = SellerInfoForm()
        return render(request=request, template_name="art/registerseller.html", context={"userform": userform,"sellerForm":sellerForm})

# user login

def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    else:
        if request.method == "POST":
            form = LoginForm(request, request.POST)

            if form.is_valid():
                uname = request.POST['username']
                upass = request.POST['password']
                user = authenticate(request, username= uname,password = upass)
                if user is not None:
                    login(request, user)
                    if user.groups.filter(name='SellerGroup').exists():
                        # return redirect(request.GET.get("next") or "dashboard:dashboard")
                        toatal_order = OrderModel.objects.filter(product__user = user).count()
                        toatal_product = Artwork.objects.filter(user = user).count()
                        return render(request=request, template_name="dashboard/dashboard.html", context={'is_Seller':True,"total_order":toatal_order,"toatal_product":toatal_product})

                    # return redirect(request.GET.get("next") or "art:index")
                    return render(request=request, template_name="dashboard/dashboard.html", context={'is_Seller':False})

            messages.error(request, form.errors)
    form = LoginForm()
    return render(request=request, template_name="art/signin.html", context={'login_form':form})


# user profile
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


class Get404View(TemplateView):
    template_name = "404.html"


class ArtworkDetailView(DetailView):
    model = Artwork
    template_name = "art/product_detail.html"

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
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Payment.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(
                request, "art/callback.html", context={"status": "Payment done"}
            )
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(
                request,
                "art/callback.html",
                context={
                    "status": "Payment done",
                    "order": order,
                    "providor": provider_order_id,
                },
            )
    else:
        # payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        # provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
        #     "order_id"
        # )
        # order = Payment.objects.get(provider_order_id=provider_order_id)
        # # order.payment_id = payment_id
        # order.status =  "Failure"
        # order.save()
        return render(request, "art/callback.html", context={"status": "order.status"})


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

    def get_queryset(self):
        return Artwork.objects.filter(end_date__lt=datetime.date.today())


# class CatListView(LoginRequiredMixin, ListView):
#     model = Product
#     template_name = "art/index.html"
#     context_object_name = "product_object_list"

#     def get_queryset(self):
#         return Product.objects.filter(product_cat=self.kwargs("id"))
