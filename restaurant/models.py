from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse

class Customer(User):
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    warnings = models.IntegerField(default=0)

    class Meta:
        permissions = [('has_vip', 'Has VIP permission')]

class Staff(User):
    class Types(models.TextChoices):
        CHEF = 'CHEF', 'Chef'
        DP = 'DP', 'Delivery Person'

    type = models.CharField(_('Type'), max_length=50, choices=Types.choices)
    # Might end up just using 1, + compliments, 0 equal, - complaints
    complaints = models.IntegerField(default=0)
    compliments = models.IntegerField(default=0)

class ChefManager(models.Manager):
     def get_queryset(self, *args, **kwargs):
         return super().get_queryset(*args, *kwargs).filter(type=Staff.Types.CHEF)

class Chef(Staff):
    options = ChefManager()

    class Meta:
        proxy = True
        permissions = [('has_desig_chef', 'Has Designated chef permission')]

class DeliveryPersonManager(models.Manager):
     def get_queryset(self, *args, **kwargs):
         return super().get_queryset(*args, *kwargs).filter(Staff.Types.DP)

class DeliveryPerson(Staff):
    options = DeliveryPersonManager()

    class Meta:
        proxy = True

class Deposit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class PaymentType(models.TextChoices):
        CARD = 'CARD', _('Credit Card')
        CRYPTO = 'CRYPTO', _('Cryptocurrency')

    payment_type = models.CharField(max_length=6, choices=PaymentType.choices, default=PaymentType.CARD)

class Menu(models.Model):
    dish_name = models.CharField(max_length=500)
    dish_chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.FloatField(default=0.0)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # Needs to be multiple dishes
    dish = models.ForeignKey(Menu, on_delete=models.CASCADE)
    chef_prepared = models.ForeignKey(Chef, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    dine_in_time = models.DateTimeField(null=True)
    order_date = models.DateTimeField()

    class Meta:
        ordering = ['-order_date']

class Post(models.Model):
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_posted = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

# Only customers
class Report(models.Model):
    snitch = models.ForeignKey(Customer, related_name='reports_snitch', on_delete=models.CASCADE)
    complainee = models.ForeignKey(Customer, related_name='reports_complainee', on_delete=models.CASCADE)
    report_body = models.TextField()
    dispute_body = models.TextField()
    is_disputed = models.BooleanField(default = False)

class UnproccessedComplaint(models.Model):
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

    def resolveSnitchType(self):
        if self.snitch_type == UnproccessedComplaint.SnitchType.CUSTOMER:
            return Customers.objects.get(pk=self.complainee_id)
        else:
            return DeliveryPerson.objects.get(pk=self.complainee_id)

    def resolveComplaineeType(self):
        if self.complainee_type == UnproccessedComplaint.ComplaineeType.CUSTOMER:
            return Customer.objects.get(pk=self.complainee_id)
        elif self.complainee_type == UnproccessedComplaint.ComplaineeType.DP:
            return DeliveryPerson.objects.get(pk=self.complainee_id)
        else:
            return Chef.objects.get(pk=self.complainee_id)
