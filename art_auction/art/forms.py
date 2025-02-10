from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from art.models import SellerInfo, UserInfo
from dashboard.models import Artwork, Feedback, Catalogue, PurchaseCategory
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    phone_number = forms.CharField(required=True, help_text="Please enter the phone number without +91")
    password1 = forms.CharField(
        label="Password", 
        required=True, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password", 
        required=True, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
    
    # Print form fields for debugging
        print("Form fields before modification:", self.fields.keys())
    
    # Remove unnecessary fields
        if 'usable_password' in self.fields:
            del self.fields['usable_password']
    
    # Add consistent styling to other fields
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "phone_number", "password1", "password2")
        
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Check if UserInfo already exists before creating
            UserInfo.objects.get_or_create(user=user, defaults={'phone_number': self.cleaned_data['phone_number']})
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        fields = ("username", "password")

class SellerInfoForm(forms.ModelForm):
    # phone_number = forms.CharField(required=True, help_text="Please enter the phone number without +91")

    def __init__(self, *args, **kwargs):
        super(SellerInfoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = SellerInfo
        fields = ("business_name",)
        widgets = {'user': forms.HiddenInput()}

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class SellerForm(forms.ModelForm):
    class Meta:
        model = SellerInfo
        fields = ['business_name']
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
class ArtworkForm(forms.ModelForm):
    discounted_price = forms.DecimalField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Artwork
        fields = [
            'sale_type', 'product_name', 'product_price', 'product_qty', 'product_image',
            'product_cat', 'purchase_category', 'product_id', 'end_date', 'opening_bid',
            'dimension_unit', 'length_in_centimeters', 'width_in_centimeters', 'foot', 'inches'
        ]
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sale_type = kwargs.get('data', {}).get('sale_type') or self.initial.get('sale_type')

        if sale_type == 'discount':
            self.fields['purchase_category'].required = True
            self.fields['purchase_category'].widget = forms.Select(choices=[(cat.id, cat.name) for cat in PurchaseCategory.objects.all()])
            self.fields['product_cat'].widget = forms.HiddenInput()
            self.fields['opening_bid'].widget = forms.HiddenInput()
            self.fields['end_date'].widget = forms.HiddenInput()
        elif sale_type == 'auction':
            self.fields['purchase_category'].required = True  # <-- Ensure it's included for auctions as well
            self.fields['product_cat'].required = True
            self.fields['opening_bid'].required = True
            self.fields['end_date'].required = True

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            
        # Ensure product_cat, opening_bid, and end_date fields are always present
        if 'product_cat' not in self.fields:
            self.fields['product_cat'] = forms.ModelChoiceField(queryset=Catalogue.objects.all())
            
        if 'purchase_category' not in self.fields:
            self.fields['purchase_category'] = forms.ModelChoiceField(queryset=PurchaseCategory.objects.all(), required=False)
    
        if 'opening_bid' not in self.fields:
            self.fields['opening_bid'] = forms.DecimalField(required=False)
    
        if 'end_date' not in self.fields:
            self.fields['end_date'] = forms.DateField(required=False)
    
        if sale_type == 'discount':
            # Make fields optional and hide them
            self.fields['product_cat'].required = False
            self.fields['opening_bid'].required = False
            self.fields['end_date'].required = False
            self.fields['product_cat'].widget = forms.HiddenInput()
            self.fields['opening_bid'].widget = forms.HiddenInput()
            self.fields['end_date'].widget = forms.HiddenInput()
    
            self.fields['purchase_category'].required = True  # Require purchase category for discount type
            # Set discounted_price value
            if self.instance and self.instance.product_price:
                self.initial['discounted_price'] = self.instance.product_price * 0.7
    
        elif sale_type == 'auction':
            # Ensure auction-specific fields are visible and required
            self.fields['discounted_price'].widget = forms.HiddenInput()
            self.fields['product_cat'].required = True
            self.fields['opening_bid'].required = True
            self.fields['end_date'].required = True
            
            self.fields['purchase_category'].required = False  # Purchase category not required for auctions
            self.fields['purchase_category'].widget = forms.HiddenInput()
    
        # Apply consistent form-control styling
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super().clean()
        sale_type = cleaned_data.get('sale_type')

        if sale_type == 'auction':
            cleaned_data.pop('purchase_category', None)  # Ensure it’s removed
        
        if sale_type == 'discount':
            # Ensure these fields are ignored for discount type
            cleaned_data['product_cat'] = None
            cleaned_data['opening_bid'] = None
            cleaned_data['end_date'] = None
            
        if not cleaned_data.get('purchase_category'):
            self.add_error('purchase_category', "Purchase category is required for discounts.")

        elif sale_type == 'auction':
            # Validate auction-specific fields
            if not cleaned_data.get('product_cat'):
                self.add_error('product_cat', "Product category is required for bidding.")
            if not cleaned_data.get('opening_bid'):
                self.add_error('opening_bid', "Opening bid is required for bidding.")
            if not cleaned_data.get('end_date'):
                self.add_error('end_date', "End date is required for bidding.")

        return cleaned_data


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'feedback_text']