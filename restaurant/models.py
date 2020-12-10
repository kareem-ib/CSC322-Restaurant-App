from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.db.models import F

DINING_CHOICES = (
    ('DI', 'Dine In'),
    ('D', 'Delivery'),
    ('P', 'Pickup')
)

TAG_CHOICES = (
    ('SP', 'Specials'),
    ('A', 'Appetizers'),
    ('S', 'Salads'),
    ('C', 'Chicken'),
    ('B', 'Beef'),
    ('P', 'Pork'),
    ('D', 'Desserts')
)

class Customer(User):
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    warnings = models.IntegerField(default=0)

    def inc_warning(self):
        self.warnings = F('warnings') + 1
        self.save()
        self.check_warnings()

    def check_warnings(self):
        for cust in Customer.objects.filter(warnings__gte=3):
            cust.delete()

    def get_customer(id):
        return Customer.objects.get(pk=id)

    def get_cart(self):
        cart = []
        for item in self.menuitems_set.all():
            cart.append({'item': item.item.name,
            'price': item.quantity * item.item.price,
            'quantity': item.quantity})
        return cart

    def get_cart_price(self):
        price = 0
        for item in self.menuitems_set.all():
            price = price + item.quantity * item.item.price
        return price

    class Meta:
        permissions = [('has_vip', 'Has VIP permission')]

class Staff(User):
    """class Types(models.TextChoices):
        CHEF = 'CHEF', 'Chef'
        DP = 'DP', 'Delivery Person'"""

    #type = models.CharField(_('Type'), max_length=50, choices=Types.choices)
    # Might end up just using 1, + compliments, 0 equal, - complaints
    complaints = models.IntegerField(default=0)
    compliments = models.IntegerField(default=0)
    salary = models.DecimalField(max_digits=7, decimal_places=2, default=12500)

    class Meta:
        abstract = True

"""class ChefManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, *kwargs).filter(type=Staff.Types.CHEF)

    def create(self, **kwargs):
        kwargs.update({"type": "CHEF"})
        return super(ChefManager, self).create(**kwargs)"""

class Chef(Staff):
    #objects = ChefManager()

    def is_desig_chef(self):
        return self.has_perm('restaurant.has_desig_chef')

    class Meta:
        permissions = [('has_desig_chef', 'Has Designated chef permission')]

"""class DeliveryPersonManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, *kwargs).filter(Staff.Types.DP)
    def create(self, **kwargs):
        kwargs.update({"type": "DP"})
        return super(DeliveryPersonManager, self).create(**kwargs)"""

class DeliveryPerson(Staff):
    #objects = DeliveryPersonManager()

    """class Meta:
        proxy = True"""

class Deposit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class PaymentType(models.TextChoices):
        CARD = 'CARD', _('Credit Card')
        CRYPTO = 'CRYPTO', _('Cryptocurrency')

    payment_type = models.CharField(max_length=6, choices=PaymentType.choices, default=PaymentType.CARD)

class Dish(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    total_ratings = models.IntegerField(default=0)
    avg_ratings = models.FloatField(default=0.0)
    dish_chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    tag = models.CharField(choices=TAG_CHOICES, max_length=2)
    image = models.ImageField(upload_to='img')
    last_ordered_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'

# A given customer's active cart
class MenuItems(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(Dish, on_delete=models.CASCADE)
    #ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return '{}, {}'.format(self.item.name, str(self.quantity))

    def update_item_date(self):
        self.item.last_ordered_date = timezone.now()
        self.item.save()


"""class Cart(models.Model):
    customer = models.OneToOneField(Customer, primary_key=True, on_delete=models.CASCADE)
    dishes = models.ManyToManyField(MenuItems)

    def get_running_cost(self):
        cost = 0
        for dish in self.dishes.all():
            cost += dish.item.cost * dish.quantity
        return cost"""

class Orders(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    #dishes = models.ManyToManyField(MenuItems)
    chef_prepared = models.ForeignKey(Chef, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    dine_in_time = models.DateTimeField(null=True)
    order_date = models.DateTimeField(default=timezone.now)
    dining_option = models.CharField(choices=DINING_CHOICES, max_length=2, default='D')
    delivery_address = models.CharField(max_length=200, null=True)

    class Meta:
        ordering = ['-order_date']

class Post(models.Model):
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_posted = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=200)
    body = models.TextField(max_length=2000)

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
    time_reported = models.DateTimeField(default=timezone.now)

    def accept_report(self):
        self.complainee.inc_warning()
        self.delete()

    def deny_report(self):
        self.snitch.inc_warning()
        self.delete()

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
