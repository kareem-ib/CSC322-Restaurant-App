from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.db.models import F, Sum

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

SENDER_CHOICES = (
    ('C', 'Customer'),
    ('DP', 'Delivery Person')
)

RECIPIENT_CHOICES = (
    ('C', 'Customer'),
    ('DP', 'Delivery Person'),
    ('CH', 'Chef')
)

CC_CHOICES = (
    ('CA', 'Complaint'),
    ('CI', 'Compliment')
)

class Customer(User):
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    warnings = models.IntegerField(default=0)
    is_VIP = models.BooleanField(default=False)

    def inc_warning(self):
        self.warnings = F('warnings') + 1
        self.save()
        self.check_warnings()

    def dec_warning(self):
        # Customer's warnings can be negative. This implies that compliments
        # can be stored to cancel out future warnings.
        self.warnings = F('warnings') - 1
        self.save()
        self.check_warnings()

    def check_warnings(self):
        if self.is_VIP:
            for cust in Customer.objects.filter(pk=self.pk, warnings__gte=2):
                cust.is_VIP = False
                cust.save()
        else:
            Customer.objects.filter(pk=self.pk, warnings__gte=3).delete()

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

    def is_customer(user):
        return hasattr(user, 'customer')

    def check_vip(self):
        orders = Orders.objects.filter(customer = self)
        if len(orders) >= 50 or orders.aggregate(Sum('cost'))['cost__sum'] >= 500:
            self.is_VIP = True
            self.save()

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class Staff(User):
    """class Types(models.TextChoices):
        CHEF = 'CHEF', 'Chef'
        DP = 'DP', 'Delivery Person'"""

    # Complaints is used as a counter for both compliments and complaints.
    # A negative value implies the given staff member has more compliments
    # than complaints.
    complaints = models.IntegerField(default=0)
    salary = models.DecimalField(max_digits=7, decimal_places=2, default=12500)
    demotions = models.IntegerField(default=0)

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

    def is_chef(user):
        return hasattr(user, 'chef')

    def is_desig_chef(self):
        return self.has_perm('restaurant.has_desig_chef')

    def inc_complaint(self):
        self.complaints = F('complaints') + 1
        self.save()
        self.check_demotion()

    def dec_complaint(self):
        # Staff's complaints can be negative. This implies that compliments
        # can be stored to cancel out future complaints.
        self.complaints = F('complaints') - 1
        self.save()
        self.check_promotion()

    def check_demotion(self):
        for chef in Chef.objects.filter(complaints__gte=3):
            chef.complaints = F('complaints') - 3
            # 20% decrease upon demotion
            chef.salary = F('salary') * 0.8
            chef.demotions = F('demotions') + 1
            chef.save()
        self.check_fired()

    def check_fired(self):
        Chef.objects.filter(demotions__gte=2).delete()

    def check_promotion(self):
        for chef in Chef.objects.filter(complaints__lte=-3):
            chef.complaints = F('complaints') + 3
            # 10% increase upon promotion
            chef.salary = F('salary') * 1.1
            chef.save()

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

    def is_dp(user):
        return hasattr(user, 'deliveryperson')

    def inc_complaint(self):
        self.complaints = F('complaints') + 1
        self.save()
        self.check_demotion()

    def dec_complaint(self):
        # Staff's complaints can be negative. This implies that compliments
        # can be stored to cancel out future complaints.
        self.complaints = F('complaints') - 1
        self.save()
        self.check_promotion()

    def check_demotion(self):
        for dp in DeliveryPerson.objects.filter(complaints__gte=3):
            dp.complaints = F('complaints') - 3
            # 20% decrease upon demotion
            dp.salary = F('salary') * 0.8
            dp.demotions = F('demotions') + 1
            dp.save()
        self.check_fired()

    def check_fired(self):
        DeliveryPerson.objects.filter(demotions__gte=2).delete()

    def check_promotion(self):
        for dp in DeliveryPerson.objects.filter(complaints__lte=-3):
            dp.complaints = F('complaints') + 3
            # 10% increase upon promotion
            dp.salary = F('salary') * 1.1
            dp.save()

    class Meta:
        verbose_name = 'Delivery Person'
        verbose_name_plural = 'Delivery People'

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
    num_of_orders = models.IntegerField(default=0)

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
        print(timezone.now())
        print('sdgsdgsdgsdgsd')
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
    dishes = models.ManyToManyField(Dish)
    chef_prepared = models.ForeignKey(Chef, on_delete=models.SET_NULL, null=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    dine_in_time = models.DateTimeField(null=True)
    order_date = models.DateTimeField(default=timezone.now)
    dining_option = models.CharField(choices=DINING_CHOICES, max_length=2, default='D')
    delivery_address = models.CharField(max_length=200, null=True)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True)

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
    report_body = models.TextField(max_length=2000)
    dispute_body = models.TextField(max_length=2000)
    is_disputed = models.BooleanField(default = False)
    time_reported = models.DateTimeField(default=timezone.now)

    def accept_report(self):
        self.complainee.inc_warning()
        self.delete()

    def deny_report(self):
        self.snitch.inc_warning()
        self.delete()

class Compliments(models.Model):
    sender = models.ForeignKey(User, related_name='compliments_sender', default=1, on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, related_name='compliments_recipient', default=1, on_delete=models.SET_NULL, null=True)
    body = models.TextField(max_length=2000)
    is_processed = models.BooleanField(default=False)

    def accept_compliment(self):
        if Customer.is_customer(self.recipient):
            Customer.get_customer(self.recipient.id).dec_warning()
        elif Chef.is_chef(self.recipient):
            Chef.objects.get(pk=self.recipient.id).dec_complaint()
        else:
            DeliveryPerson.objects.get(pk=self.recipient.id).dec_complaint()
        self.is_processed = True
        self.save()


    def deny_compliment(self):
        self.is_processed = True
        self.save()

    class Meta:
        verbose_name = 'Compliment'
        verbose_name_plural = 'Compliments'

class Complaints(models.Model):
    sender = models.ForeignKey(User, related_name='complaints_sender', default=1, on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, related_name='complaints_recipient', default=1, on_delete=models.SET_NULL, null=True)
    complaint_body = models.TextField(max_length=2000)
    dispute_body = models.TextField(max_length=2000)
    is_disputed = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    def accept_complaint(self):
        if not self.recipient:
            self.delete()
            return
        if Customer.is_customer(self.recipient):
            Customer.get_customer(self.recipient.id).inc_warning()
        elif Chef.is_chef(self.recipient):
            chef = Chef.objects.get(pk=self.recipient.id)

            chef.inc_warning()
            if Customer.is_customer(self.sender).is_VIP:
                cust.inc_warning()
        else:
            dp = DeliveryPerson.objects.get(pk=self.recipient.id)

            dp.inc_warning()
            if Customer.is_customer(self.sender).is_VIP:
                dp.inc_warning()
        self.is_processed = True
        if not self.recipient:
            self.delete()
            return
        self.save()

    def deny_complaint(self):
        if not self.sender:
            self.delete()
            return
        if Customer.is_customer(self.sender):
            Customer.get_customer(self.sender.id).inc_warning()
        elif Chef.is_chef(self.sender):
            Chef.objects.get(pk=self.sender.id).inc_complaint()
        else:
            DeliveryPerson.objects.get(pk=self.sender.id).inc_complaint()
        self.is_processed = True
        if not self.sender:
            self.delete()
            return
        self.save()

    class Meta:
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
