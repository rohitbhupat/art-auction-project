import datetime
from django import forms
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.models import Artwork , OrderModel , Catalogue , Bid
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView ,DeleteView
from django.urls import reverse_lazy
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages



# Create your views here.

class Index(View):
    # news_obj = News()
    # post_obj = PostObject()
    # get_news = news_obj.get_top_news_headlines(language='en',country='in',page_size=5)
    
    def get(self,request):

        # return render(request,'art/index.html',{'news':self.get_news,'public_post':self.post_obj.get_all_posts().order_by('-created_on')[:5]})
        return render(request,'dashboard/dashboard.html')
    


class ArtworkCreateView(LoginRequiredMixin, CreateView):
    model = Artwork
    fields = ["product_name", "product_price", "product_image", "product_qty", "opening_bid", "product_cat", "end_date"]
    success_url = '/dashboard/product/'

    def get_form(self):
        form = super().get_form()
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def form_valid(self, form):
        # Debugging statements
        print("Form is valid")
        print("Form data:", form.cleaned_data)

        last_id = 1
        last_product = Artwork.objects.all().values('pk').last()
        if last_product:
            last_id = last_product['pk'] + 1
        print("Last ID:", last_id)

        try:
            cat = Catalogue.objects.get(pk=self.request.POST['product_cat']).cat_name[:3]
            print("Category:", cat)
        except Catalogue.DoesNotExist:
            form.add_error('product_cat', 'Invalid category')
            print("Invalid category")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.product_id = f'{cat}{last_id}'
        print("Product ID:", form.instance.product_id)

        response = super().form_valid(form)
        print("Product created successfully")
        return response

    def form_invalid(self, form):
        print("Form is invalid")
        print("Errors:", form.errors)
        return super().form_invalid(form)

class BidCreateView(LoginRequiredMixin, View):
    def post(self, request):
        bid_amt = float(request.POST["bid_amt"])
        product = request.POST["product"]
        product_object = Artwork.objects.get(pk=product)

        highest_bid = Bid.objects.filter(product=product_object).order_by("-bid_amt").first()

        if highest_bid is None:
            min_bid = product_object.opening_bid
            if bid_amt < min_bid:
                messages.error(request, "Your bid must be greater than the opening bid amount.")
                return redirect(f"/viewdetails/{product}/")
        else:
            min_bid = highest_bid.bid_amt
            if bid_amt <= min_bid:
                messages.error(request, "Your bid must be higher than the current highest bid.")
                return redirect(f"/viewdetails/{product}/")

        new_bid = Bid.objects.create(user=request.user, bid_amt=bid_amt, product=product_object)
        messages.success(request, "Your bid has been placed")

        return redirect(f"/viewdetails/{product}/")
        

class ArtworkListView(LoginRequiredMixin, ListView):
    model = Artwork
    def get_queryset(self):
        return Artwork.objects.filter(user = self.request.user)

class BidListView(LoginRequiredMixin, ListView):
    model = Bid
    template_name = 'dashboard/bids_list.html'

class ArtworkUpdateView(UpdateView):
    model = Artwork
    fields = ["Name","product_price","product_image","product_cat","end_date"]
    template_name_suffix = '_update_form'
    success_url = '/dashboard/product/'

    def get_form(self):
        form = super().get_form()
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

class ArtworkDeleteView(DeleteView):
    model = Artwork
    success_url = reverse_lazy('dashboard:product_list')


class OrderListView(LoginRequiredMixin, ListView):
    model = OrderModel
    template_name = 'dashboard/ordermodel_list.html'  # Update this to your correct template path

    def get_queryset(self):
        if self.request.user.groups.filter(name='SellerGroup').exists():
            # If the user is a seller, fetch orders for their products
            return OrderModel.objects.filter(product__user=self.request.user)
        else:
            # Otherwise, fetch orders placed by the user
            return OrderModel.objects.filter(user=self.request.user)

