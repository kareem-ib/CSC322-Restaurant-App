from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class BaseInfo(models.Model):
    f_name = models.CharField(max_length=200)
    l_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)

    class Meta:
        abstract = True

class Customers(BaseInfo):
    balance = models.DecimalField(decimal_places=2, default=0.0)
    is_VIP = models.BooleanField(default=False)
    warnings = models.IntegerField(default=0)

class Staff(BaseInfo):
    # Might end up just using 1, + compliments, 0 equal, - complaints
    complaints = models.IntegerField(default=0)
    compliments = models.IntegerField(default=0)

class Chef(Staff):
    desig_chef = models.BooleanField(default=False)

class DeliveryPerson(Staff):
    pass

class Manager(Staff):
    pass

class Deposits(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)

    class PaymentType(models.TextChoices):
        CARD = 'CARD', _('Credit Card')
        CRYPTO = 'CRYPTO', _('Cryptocurrency')

    payment_type = models.CharField(max_length=6, choices=PaymentType.choices, default=PaymentType.CARD)

class Menu(models.Model):
    dish_name = models.CharField(max_length=500)
    dish_chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2)
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.FloatField(default=0.0)

class Orders(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    # Needs to be multiple dishes
    dish = models.ForeignKey(Menu, on_delete=models.CASCADE)
    chef_prepared = models.ForeignKey(Chef, on_delete=models.CASCADE)
    cost = models.DecimalField(decimal_places=2)
    dine_in_time = models.DateTimeField(null=True)

class Posts(models.Model):
    author = models.ForeignKey(Customers, on_delete=models.CASCADE)
    time_posted = models.DateTimeField()
    subject = models.TextField()
    body = models.TextField()

# Only customers
class Reports(models.Model):
    snitch = models.ForeignKey(Customers, on_delete=models.CASCADE)
    complainee = models.ForeignKey(Customers, on_delete=models.CASCADE)
    report_body = models.TextField()
    dispute_body = models.TextField()

class UnproccessedComplaints(models.Model):
    class SnitchType(models.TextChoices):
        CUSTOMER = 'CUST', _('Customers')
        DP = 'DP', _('Delivery Person')

    class ComplaineeType(models.TextChoices):
        CUSTOMER = 'CUST', _('Customers')
        DP = 'DP', _('Delivery Person')
        CHEF = 'CHEF', _('Chef')

    snitch_type = models.CharField(max_length=4, choices=SnitchType.choices)
    snitch_id = models.IntegerField()
    complainee_type = models.CharField(max_length=4, choices=ComplaineeType.choices)
    complainee_id = models.IntegerField()
    complaint_body = models.TextField()
    dispute_body = models.TextField()