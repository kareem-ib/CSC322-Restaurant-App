from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Chef, DeliveryPerson, Post, Compliments, Complaints, Dish, Comment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit

class CommentForm(forms.ModelForm):
    body = forms.CharField(max_length=280, )

    class Meta:
        model = Comment
        fields = ['body']

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    # EmailField's required arg is True by default
    email = forms.EmailField()

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ChefRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    # EmailField's required arg is True by default
    email = forms.EmailField()

    class Meta:
        model = Chef
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class DPRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    # EmailField's required arg is True by default
    email = forms.EmailField()

    class Meta:
        model = DeliveryPerson
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=6, decimal_places=2, required=True, min_value=0)
    card_number = forms.CharField(max_length=16, required=True, widget=forms.PasswordInput)

    class Meta:
        fields = ['amount', 'card_number']

class ComplimentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs['choices']
        del kwargs['choices']
        super(ComplimentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.fields['recipient'] = forms.TypedChoiceField(
            label = "Recipient",
            choices = choices,
            coerce = lambda x: int(x),
            widget = forms.RadioSelect,
            required = True,
        )
        self.fields['body'] = forms.CharField(
            label = "Body",
            required = True,
            max_length = Compliments._meta.get_field('body').max_length
        )

    class Meta:
        model = Compliments
        fields = ['recipient', 'body']

class ComplaintForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs['choices']
        del kwargs['choices']
        super(ComplaintForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.fields['recipient'] = forms.TypedChoiceField(
            label = "Recipient",
            choices = choices,
            coerce = lambda x: int(x),
            widget = forms.RadioSelect,
            required = True,
        )
        self.fields['complaint_body'] = forms.CharField(
            label = "Body",
            required = True,
            max_length = Complaints._meta.get_field('complaint_body').max_length
        )

    class Meta:
        model = Complaints
        fields = ['recipient', 'complaint_body']

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ()

class RatingForm(DishForm):
    rating = forms.IntegerField(min_value=0, max_value=5)

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)

    class Meta(DishForm.Meta):
        fields = DishForm.Meta.fields + ('rating',)

class QuitForm(forms.Form):
    quit_request = forms.TypedChoiceField(
        label = "Please Select a Choice",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        required = True,
    )
    class Meta:
        model = Customer
        fields = ['quit_request']
