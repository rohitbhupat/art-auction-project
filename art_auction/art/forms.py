from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from art.models import SellerInfo
class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args,**kwargs):
        super(UserRegistrationForm, self).__init__(*args,**kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password1 = forms.CharField(label="Password",required=True,widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password",required=True,widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ("first_name","last_name","username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args,**kwargs):
        super(LoginForm, self).__init__(*args,**kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        fields = ("username", "password")



class SellerInfoForm(forms.ModelForm):
    def __init__(self, *args,**kwargs):
        super(SellerInfoForm, self).__init__(*args,**kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = SellerInfo
        fields = ("phone_number","business_name","user",)
        widgets = {'user':forms.HiddenInput()}    

