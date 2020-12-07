from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Post

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    # EmailField's required arg is True by default
    email = forms.EmailField()

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=6, decimal_places=2, required=True)
    card_number = forms.CharField(max_length=16, required=True, widget=forms.PasswordInput)

    class Meta:
        fields = ['amount', 'card_number']

'''class PostForm(forms.Form):
    subject = forms.CharField(max_length=200, required=True)
    body = forms.CharField(max_length=2000, required=True, widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ['subject', 'body']

class ReportForm(forms.Form):

class DisputeForm(forms.Form):

class ComplaintComplimentForm(forms.Form):'''
