from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from art.models import SellerInfo, UserInfo
from dashboard.models import Artwork, Feedback
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
    SALE_TYPE_CHOICES = [
        ('discount', 'Discount'),
        ('bidding', 'Bidding'),
    ]

    sale_type = forms.ChoiceField(
        choices=SALE_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_sale_type'}),
    )

    class Meta:
        model = Artwork
        fields = [
            'sale_type', 'product_name', 'product_price', 'product_qty', 'product_image',
            'product_cat', 'product_id', 'end_date', 'discounted_price', 'opening_bid',
            'dimension_unit', 'length_in_centimeters', 'width_in_centimeters', 'foot', 'inches'
        ]

    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)

        # Set all fields to have the 'form-control' class for consistency
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

        # Adjust the `required` attribute for fields based on the sale type
        if 'data' in kwargs and kwargs['data'].get('sale_type') == 'discount':
            self.fields['product_cat'].required = False
        else:
            self.fields['product_cat'].required = True

    def clean(self):
        cleaned_data = super().clean()
        sale_type = cleaned_data.get('sale_type')

        # Validate `product_cat` only if the sale type is 'bidding'
        if sale_type == 'bidding' and not cleaned_data.get('product_cat'):
            self.add_error('product_cat', "Product category is required for bidding.")
            
        if sale_type == 'discount' and not cleaned_data.get('discounted_price'):
            cleaned_data['discounted_price'] = cleaned_data['product_price'] * 0.7

        # Ensure `opening_bid` and `end_date` are not validated for 'discount'
        if sale_type == 'discount':
            cleaned_data['product_cat'] = None
            cleaned_data['opening_bid'] = None
            cleaned_data['end_date'] = None

        return cleaned_data

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'feedback_text']