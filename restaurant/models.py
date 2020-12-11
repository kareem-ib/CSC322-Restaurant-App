from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.db.models import F, Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, timedelta

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

"""
The Customer model.
Customers are an extension of User. They have a balance, warning counter, VIP status (initially False),
and a quit_request field which is initially False.
"""
class Customer(User):
    balance = models.DecimalField(max_digits=25, decimal_places=2, default=0.0)
    warnings = models.IntegerField(default=0)
    is_VIP = models.BooleanField(default=False)
    quit_request = models.BooleanField(default=False)

    # Increments a customer's warnings then checks his/her warnings.
    def inc_warning(self):
        self.warnings = F('warnings') + 1
        self.save()
        self.check_warnings()

    # Decrements a customer's warnings then checks his/her warnings.
    def dec_warning(self):
        # Customer's warnings can be negative. This implies that compliments
        # can be stored to cancel out future warnings.
        self.warnings = F('warnings') - 1
        self.save()
        self.check_warnings()

    # Checks if a VIP customer is set to lose their VIP status for having 2 or more warnings.
    # Checks if a customer is set to be removed from the system if he/she has 3 or more warnings.
    def check_warnings(self):
        if self.is_VIP:
            for cust in Customer.objects.filter(pk=self.pk, warnings__gte=2):
                cust.is_VIP = False
                # A VIP's warnings are reset upon losing their VIP status.
                cust.warnings = 0
                cust.save()
        else:
            Customer.objects.filter(pk=self.pk, warnings__gte=3).delete()

    # Gets the Customer for a given user ID.
    def get_customer(id):
        return Customer.objects.get(pk=id)

    # Gets the customer's current cart.
    def get_cart(self):
        cart = []
        for item in self.menuitems_set.all():
            cart.append({'item': item.item.name,
            'price': item.quantity * item.item.price,
            'quantity': item.quantity})
        return cart

    # Gets the price of the Customer's cart.
    def get_cart_price(self):
        price = 0
        for item in self.menuitems_set.all():
            price = price + item.quantity * item.item.price
        return price

    # Checks if the user is a Customer.
    def is_customer(user):
        return hasattr(user, 'customer')

    # Checks if the customer is elligible for VIP status. A customer becomes a VIP if they place
    # 50 orders or spend $500, whichever comes first.
    def check_vip(self):
        orders = Orders.objects.filter(customer = self)
        if len(orders) >= 50 or orders.aggregate(Sum('cost'))['cost__sum'] >= 500:
            self.is_VIP = True
            self.save()

    # Sets the naming convention for Customer in the admin page.
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

"""
The Staff model.
A staff member has a salary and a counter for both complaints and demotions.
"""
class Staff(User):
    # Complaints is used as a counter for both compliments and complaints.
    # A negative value implies the given staff member has more compliments
    # than complaints.
    complaints = models.IntegerField(default=0)
    salary = models.DecimalField(max_digits=7, decimal_places=2, default=12500)
    demotions = models.IntegerField(default=0)

    # The Staff model is an abstract class.
    class Meta:
        abstract = True

"""
The Chef model.
A Chef is a type of Staff.
"""
class Chef(Staff):
    # Checks if the user is a chef.
    def is_chef(user):
        return hasattr(user, 'chef')

    # Checks if the chef has the designated chef permission.
    def is_desig_chef(self):
        return self.has_perm('restaurant.has_desig_chef')

    # Increments the delivery person's complaints, then checks if he/she is set for a demotion.
    def inc_complaint(self):
        self.complaints = F('complaints') + 1
        self.save()
        self.check_demotion()

    # Decrements the chef's complaints, then checks if he/she is set for a promotion.
    def dec_complaint(self):
        # Staff's complaints can be negative. This implies that compliments
        # can be stored to cancel out future complaints.
        self.complaints = F('complaints') - 1
        self.save()
        self.check_promotion()

    # Checks if the chef is set for a promotion when their complaints are greater than
    # or equal to 3.
    def check_demotion(self):
        self.check_ratings()
        for chef in Chef.objects.filter(complaints__gte=3):
            chef.complaints = F('complaints') - 3
            # 20% decrease upon demotion
            self.demote(chef)
            chef.save()

    def demote(self, chef):
        chef.salary = F('salary') * 0.8
        chef.demotions = F('demotions') + 1
        chef.check_fired()

    # Checks if the chef is elligible for being fired (when they have been demoted twice).
    def check_fired(self):
        Chef.objects.filter(demotions__gte=2).delete()

    # Checks if the chef is set for a promotion when their complaints are less
    # than or equal to -3 (which is the same as 3 compliments).
    def check_promotion(self):
        self.check_ratings()
        for chef in Chef.objects.filter(complaints__lte=-3):
            # reset these 3 compliments
            chef.complaints = F('complaints') + 3
            # 10% increase upon promotion
            self.promote(chef)
            chef.save()

    def promote(self, chef):
        chef.salary = F('salary') * 1.1

    def check_ratings(self):
        today = timezone.now()
        past_3_days = today - timedelta(days=3)

        for dish in self.dish_set.all():
            total_ratings = dish.total_ratings
            avg_ratings = dish.avg_ratings

            if dish.last_ordered_date < past_3_days or (total_ratings % 10 == 0 and avg_ratings <= 2.0):
                self.demote(self)
            
            if (total_ratings % 10 == 0 and avg_ratings >= 4.0):
                self.promote(self)

    # Sets a designated chef permission for Chefs. If a given chef has this permission, he/she is
    # granted access to the admin page where they can only add dishes.
    class Meta:
        permissions = [('has_desig_chef', 'Has Designated chef permission')]

"""
The DeliveryPerson model
A DeliveryPerson is a type of Staff. A DeliveryPerson also has their own ratings which can be updated
by Customers.
"""
class DeliveryPerson(Staff):
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    number_ratings = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0)
    
    # Checks if the user is a delivery person.
    def is_dp(user):
        return hasattr(user, 'deliveryperson')

    # Increments the delivery person's complaints, then checks if he/she is set for a demotion.
    def inc_complaint(self):
        self.complaints = F('complaints') + 1
        self.save()
        self.check_demotion()

    # Decrements the delivery person's complaints, then checks if he/she is set for a promotion.
    def dec_complaint(self):
        # Staff's complaints can be negative. This implies that compliments
        # can be stored to cancel out future complaints.
        self.complaints = F('complaints') - 1
        self.save()
        self.check_promotion()

    # Checks if the delivery person is set for a promotion when their complaints are greater than
    # or equal to 3.
    def check_demotion(self):
        for dp in DeliveryPerson.objects.filter(complaints__gte=3):
            dp.complaints = F('complaints') - 3
            # 20% decrease upon demotion
            dp.salary = F('salary') * 0.8
            dp.demotions = F('demotions') + 1
            dp.save()
        self.check_fired()

    # Checks if the delivery person is elligible for being fired (when they have been demoted twice).
    def check_fired(self):
        DeliveryPerson.objects.filter(demotions__gte=2).delete()

    # Checks if the delivery person is set for a promotion when their complaints are less
    # than or equal to -3 (which is the same as 3 compliments).
    def check_promotion(self):
        for dp in DeliveryPerson.objects.filter(complaints__lte=-3):
            dp.complaints = F('complaints') + 3
            # 10% increase upon promotion
            dp.salary = F('salary') * 1.1
            dp.save()

    # Sets the naming convention for DeliveryPerson in the admin page.
    class Meta:
        verbose_name = 'Delivery Person'
        verbose_name_plural = 'Delivery People'

"""
The Deposit model.
A Deposit belongs to one customer, but a customer can make many deposits. When a customer is
deleted, all their deposits are deleted as well.
A given deposit has an amount which the customer inputs when making a deposit.
"""
class Deposit(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

"""
The Dish model.
The dish_chef is a designated chef who has a one to many relationship with the Dish model.
The designated chef sets the name, price, description, tag, and image through the admin page.
The Dish's ratings, number of orders, and last_ordered_date are updated automatically every time
a dish is ordered.
"""
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

    # Sets the naming convention for Dish in the admin page.
    class Meta:
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'

"""
The Rating model.
A rating has a one to many relationship to a Dish, hence the foreign key for dish.
The rating attribute has a minimum value of 0 and a maximum value of 5 for the user to input on the rate page.
"""
class Rating(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

"""
The MenuItems model.
A MenuItems instance serves as a customer's current cart.
The cart has a one to many relationship with Customer and Dish, hence the foreign keys for customer and item.
Each MenuItem in the cart also has a quantity - the number of times the user added a certain dish to the cart.
"""
class MenuItems(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return '{}, {}'.format(self.item.name, str(self.quantity))

    # Updates the last_ordered_date of the given item. This allows for checking when a designated chef
    # should be demoted for having dishes that aren't ordered frequently.
    def update_item_date(self):
        print(timezone.now())
        #print('sdgsdgsdgsdgsd')
        self.item.last_ordered_date = timezone.now()
        self.item.save()

"""
The Orders model.
An order has a one to many relation with customers, chefs, and delivery people, hence the foreign keys for the
customer, chef_prepared, and delivery_person. Based on the customer's dining option, there may or may not be a
delivery person, hence null=True for them.
An order has a total cost of all dishes in the customer's cart.
When choosing the dining option, the customer sets the dine_in_time if the dining option is 'DI' for dine in or
the delivery_address if the option is 'D' for delivery.
"""
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

    # Sets the naming convention and ordering for Orders in the admin page.
    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

"""
The Post model.
A post has a one to many relation with a customer, hence the foreign key for the author. When a customer is
deleted, all of his/her posts are deleted as well.
A customer fills in the subject and body of the post.
"""
class Post(models.Model):
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_posted = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=200)
    body = models.TextField(max_length=2000)

    def __str__(self):
        return self.subject

    # Sets the custom URL to be of form post_detail/<int:pk>
    # Where the pk is the primary key of the Post.
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

"""
The Comment model.
A comment has a one to many relation with a customer, hence the foreign key. When a customer is deleted, all
their comments are removed from the discussion board as well with the on_delete=models.CASCADE option.
A comment also has a one to many relation with a post, hence the foreign key. When the post is deleted, all
comments attached to it are deleted as well.
A customer fills in the body of the comment on the parent post's page.
"""
class Comment(models.Model):
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_posted = models.DateTimeField(default=timezone.now)
    body = models.TextField(max_length=280)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # Sets the naming convention and ordering for comments in the admin page.
    class Meta:
        ordering = ['-time_posted']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

"""
The TabooWords model.
Each entry in the table is just a word of a max_length of 50.
This model can be accessed through the admin page, where the manager can actively change the list of taboo
words.
"""
class TabooWords(models.Model):
    word = models.CharField(max_length=50)

    def __str__(self):
        return self.word

    # Sets the naming convention for the TabooWords in the admin page.
    class Meta:
        verbose_name = 'Taboo Word'
        verbose_name_plural = 'Taboo Words'

"""
The Report model.
A report has a one to many relation with the snitch and the complainee, hence the foreign keys. Reports are
only made by customers, and the complainees can only be customers. Customers can only report other customers
for misbehaving on the discussion board.
When filing a report, the customer is prompted to provide their reasoning for the report in the report_body.
The complainee has the option to dispute the complaint by providing their own reasoning through the dispute_body.
When the dispute is sent, is_disputed is changed from the default of False to True.
"""
class Report(models.Model):
    snitch = models.ForeignKey(Customer, related_name='reports_snitch', on_delete=models.CASCADE)
    complainee = models.ForeignKey(Customer, related_name='reports_complainee', on_delete=models.CASCADE)
    report_body = models.TextField(max_length=2000)
    dispute_body = models.TextField(max_length=2000)
    is_disputed = models.BooleanField(default = False)
    time_reported = models.DateTimeField(default=timezone.now)

    # Accepts a report - accessed through the admin page only.
    # Increments the complainee/recipient's warnings then deletes the report.
    def accept_report(self):
        self.complainee.inc_warning()
        self.delete()

    # Denies a report - accessed through the admin page only.
    # Increments the snitch/sender's warnings then deletes the report.
    def deny_report(self):
        self.snitch.inc_warning()
        self.delete()

"""
The Compliments model.
A complaint has a one to many relation with the sender and recipient, hence the foreign keys. Both the sender and
recipient are users; however, the sender can only be a customer or delivery person. The recipient can be a customer,
delivery person, or chef.
When a compliment is made, the sender must fill in the body of the compliment to provide any reasoning for filing the
compliment.
"""
class Compliments(models.Model):
    sender = models.ForeignKey(User, related_name='compliments_sender', default=1, on_delete=models.SET_NULL, null=True)
    recipient = models.ForeignKey(User, related_name='compliments_recipient', default=1, on_delete=models.SET_NULL, null=True)
    body = models.TextField(max_length=2000)

    # Accepts a compliment - accessed through the admin page only.
    def accept_compliment(self):
        # If the recipient is a customer, his/her warnings are decremented since a compliment
        # can be used to cancel out a warning.
        if Customer.is_customer(self.recipient):
            Customer.get_customer(self.recipient.id).dec_warning()
        # If the recipient is a chef, his/her complaints are decremented since a compliment
        # can be used to cancel out a complaint.
        elif Chef.is_chef(self.recipient):
            chef = Chef.objects.get(pk=self.recipient.id)

            chef.dec_complaint()
            # If the sender is a VIP, the compliment is counted twice.
            if Customer.is_customer(self.sender) and Customer.objects.get(pk=self.sender.id).is_VIP:
                chef.dec_complaint()
        # The recipient is a delivery person, so his/her complaints are decremented.
        else:
            dp = DeliveryPerson.objects.get(pk=self.recipient.id)

            dp.dec_complaint()
            # If the sender is a VIP, the compliment is counted twice.
            if Customer.is_customer(self.sender).is_VIP and Customer.objects.get(pk=self.sender.id).is_VIP:
                dp.dec_complaint()

        self.delete()

    # When a compliment is denied by the manager, it is simply deleted since the compliment does not count
    # towards the recipient's compliment counter.
    def deny_compliment(self):
        self.delete()

    # Sets the naming convention for the compliments in the admin page.
    class Meta:
        verbose_name = 'Compliment'
        verbose_name_plural = 'Compliments'

"""
The Complaints model.
A complaint has a one to many relation with the sender and recipient, hence the foreign keys. Both the sender
and recipient are users; however, the sender can only be a customer or delivery person. On the other hand, the
recipient can be a customer, delivery person, or chef.
When a complaint is made, the sender must provide a reasoning which is held by the complaint_body attribute.
Similarly, the recipient has the option to dispute the complaint, providing their reasoning for disputing the
complaint in the dispute_body.
When a complaint is created, it is initially not disputed, so the default for is_disputed is False. When the
dispute_body is filled in by the recipient, is_disputed is set to True.
"""
class Complaints(models.Model):
    sender = models.ForeignKey(User, related_name='complaints_sender', default=1, on_delete=models.CASCADE)#, null=True)
    recipient = models.ForeignKey(User, related_name='complaints_recipient', default=1, on_delete=models.CASCADE)#, null=True)
    complaint_body = models.TextField(max_length=2000)
    dispute_body = models.TextField(max_length=2000)
    is_disputed = models.BooleanField(default=False)

    # Accepts a complaint - accessed through the admin page only.
    def accept_complaint(self):
        # If the recipient is None, delete the complaint
        if not self.recipient:
            self.delete()
            return
        # If the recipient is a customer, increment that customer's warnings.
        if Customer.is_customer(self.recipient):
            Customer.get_customer(self.recipient.id).inc_warning()
        # If the recipient is a chef, increment that chef's warnings
        elif Chef.is_chef(self.recipient):
            chef = Chef.objects.get(pk=self.recipient.id)

            chef.inc_complaint()
            # If the sender is a VIP customer, their complaints have double the weight. So, the chef's
            # warnings are incremented again.
            if Customer.is_customer(self.sender) and Customer.objects.get(pk=self.sender.id).is_VIP:
                chef.inc_complaint()
        # The recipient must be a delivery person, so increment his/her warnings.
        else:
            dp = DeliveryPerson.objects.get(pk=self.recipient.id)

            dp.inc_complaint()
            # If the sender is a VIP customer, their complaints have double the weight. So, the delivery
            # person's warnings are incremented again.
            if Customer.is_customer(self.sender) and Customer.objects.get(pk=self.sender.id).is_VIP:
                dp.inc_complaint()

        # The complaint has been fully processed, so it can be deleted.
        self.delete()

    # Denies a complaint - accessed through the admin page only.
    def deny_complaint(self):
        # If the recipient is None, delete the complaint
        if not self.sender:
            self.delete()
            return
        # If the sender is a customer, increment that customer's warnings.
        if Customer.is_customer(self.sender):
            Customer.get_customer(self.sender.id).inc_warning()
        # The sender is a delivery person, so increment his/her complaints.
        else:
            DeliveryPerson.objects.get(pk=self.sender.id).inc_complaint()

        # The complaint has been fully processed, so it can be deleted.
        self.delete()

    # Sets the naming convention for Complaints in the admin page.
    class Meta:
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
