from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Customers(User):
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
    price = models.DecimalField(max_digits=6, decimal_places=2)
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.FloatField(default=0.0)

class Orders(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    # Needs to be multiple dishes
    dish = models.ForeignKey(Menu, on_delete=models.CASCADE)
    chef_prepared = models.ForeignKey(Chef, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    dine_in_time = models.DateTimeField(null=True)
    order_date = models.DateTimeField()

    class Meta:
        ordering = ['-order_date']

class Posts(models.Model):
    author = models.ForeignKey(Customers, on_delete=models.CASCADE)
    time_posted = models.DateTimeField()
    subject = models.TextField()
    body = models.TextField()

# Only customers
class Reports(models.Model):
    snitch = models.ForeignKey(Customers, related_name='reports_snitch', on_delete=models.CASCADE)
    complainee = models.ForeignKey(Customers, related_name='reports_complainee', on_delete=models.CASCADE)
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

    def resolveSnitchType(self):
        if self.snitch_type == UnproccessedComplaints.SnitchType.CUSTOMER:
            return Customers.objects.get(pk=self.complainee_id)
        else:
            return DeliveryPerson.objects.get(pk=self.complainee_id)

    def resolveComplaineeType(self):
        if self.complainee_type == UnproccessedComplaints.ComplaineeType.CUSTOMER:
            return Customers.objects.get(pk=self.complainee_id)
        elif self.complainee_type == UnproccessedComplaints.ComplaineeType.DP:
            return DeliveryPerson.objects.get(pk=self.complainee_id)
        else:
            return Chef.objects.get(pk=self.complainee_id)

