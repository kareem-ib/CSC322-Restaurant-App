from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm, DepositForm, ComplimentForm, ComplaintForm, RatingForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import User, Customer, Post, Report, Dish, Orders, Chef, DeliveryPerson, Compliments, Complaints, Rating, TAG_CHOICES, TabooWords
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.db.models import F
from random import randrange
from uuid import uuid4
from django.forms import DateInput
from django import forms
from decimal import Decimal
from django.http import HttpResponseForbidden

# Create your views here.

"""
Function-based view for the index page.
"""
def index(request):
    return render(request, 'restaurant/index.html')

"""
Function-based view for the about page.
"""
def about(request):
    return render(request, 'restaurant/about.html')

"""
Class-based FormView for filing a compliment for another user you have interacted with.
"""
class ComplimentCreateView(FormView):
    model = Compliments
    template_name = 'restaurant/compliment.html'
    # References the form ComplimentForm in forms.py
    form_class = ComplimentForm

    def get_success_url(self):
        return reverse('home')

    # Overrides the **kwargs for the given view.
    # Returns the list of users that the user viewing the page can file a compliment for.
    def get_form_kwargs(self):
        kwargs = super(ComplimentCreateView, self).get_form_kwargs()
        user = self.request.user

        sender = None
        if Customer.is_customer(user):
            sender = user.customer
        elif DeliveryPerson.is_dp(user):
            sender = user.deliveryperson
        else:
            redirect('home')

        orders = sender.orders_set.all()
        lst = []
        for order in orders:
            if type(sender) == Customer:
                lst.append((order.chef_prepared.user_ptr.pk, order.chef_prepared.get_full_name()))
                if order.delivery_person:
                    lst.append((order.delivery_person.user_ptr.pk, order.delivery_person.get_full_name()))
            else:
                lst.append((order.customer.user_ptr.pk, order.customer.get_full_name()))
        lst = tuple(dict.fromkeys(lst))
        kwargs['choices'] = lst
        return kwargs

    # Overrides the form_valid() function.
    def form_valid(self, form):
        print("form valid")
        self.request.user.compliments_sender.create(recipient=User.objects.get(pk=form.cleaned_data.get('recipient')),
                                                    body=form.cleaned_data.get('body'))

        messages.success(self.request, "Your compliment has been received!")
        return super().form_valid(form)

"""
Class-based FormView for filing a complaint for another user you have interacted with.
"""
class ComplaintCreateView(FormView):
    model = Complaints
    template_name = 'restaurant/complaint.html'
    # References the form ComplaintForm in forms.py
    form_class = ComplaintForm

    # Redirect the user back to the home page upon submitting a complaint successfully.
    def get_success_url(self):
        return reverse('home')

    # Overrides the **kwargs for the given view.
    # Returns the list of users that the user viewing the page can file a complaint for.
    def get_form_kwargs(self):
        kwargs = super(ComplaintCreateView, self).get_form_kwargs()
        user = self.request.user

        sender = None
        if Customer.is_customer(user):
            sender = user.customer
        elif DeliveryPerson.is_dp(user):
            sender = user.deliveryperson
        else:
            redirect('home')

        orders = sender.orders_set.all()
        lst = []
        for order in orders:
            if type(sender) == Customer:
                lst.append((order.chef_prepared.user_ptr.pk, order.chef_prepared.get_full_name()))
                if order.delivery_person:
                    lst.append((order.delivery_person.user_ptr.pk, order.delivery_person.get_full_name()))
            else:
                lst.append((order.customer.user_ptr.pk, order.customer.get_full_name()))

        lst = tuple(dict.fromkeys(lst))
        kwargs['choices'] = lst
        return kwargs

    # Overrides the form_valid() function.
    def form_valid(self, form):
        print("form valid")
        self.request.user.complaints_sender.create(recipient=User.objects.get(pk=form.cleaned_data.get('recipient')),
                                                   complaint_body=form.cleaned_data.get('complaint_body'))

        messages.success(self.request, "Your complaint has been received!")
        return super().form_valid(form)

"""
Function-based view for the deposit page.
"""
@login_required
def deposit(request):
    customer = Customer.objects.get(pk=request.user.id)
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            customer.balance = customer.balance + form.cleaned_data.get('amount')
            customer.save()
            customer.deposit_set.create(amount=customer.balance)
            messages.success(request, "The amount has been added to your balance!")
            print(form.fields)
    else:
        form = DepositForm()
    context = {
        'balance': customer.balance,
        'form': form
    }
    return render(request, 'restaurant/deposit.html', context)

"""
Class-based ListView for the discussion board.
"""
class DiscussionBoardView(ListView):
    model = Post
    template_name = 'restaurant/discussion_board.html'
    context_object_name = 'posts'
    ordering = ['-time_posted']

"""
Function-based view for the home page.
"""
def home(request):
    return render(request, 'restaurant/main_page.html')

"""
Function-based view for the user login page.
"""
def login(request):
    return render(request, 'restaurant/login.html')

"""
filter_taboo_words(text) takes in a string of text and replaces all taboo words with "***"
"""
def filter_taboo_words(text):
    split_text = text.split()
    total_taboo_words = 0
    print('TEXT:', text, 'SPLIT', split_text)
    for i, word in enumerate(split_text):
        if TabooWords.objects.filter(word = word):
            split_text[i] = '***'
            total_taboo_words += 1

    return ' '.join(split_text), total_taboo_words

"""
Class-based DetailView for viewing a specific post on the discussion board.
Allows Customers to add comments to a post.
"""
class SpecificPostView(FormMixin, DetailView):
    model = Post
    template_name = 'restaurant/post_detail.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.author = self.request.user.customer
        form.instance.post = self.object
        form.save()
        return super(SpecificPostView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment_set.all()
        context['singular'] = len(context['comments']) == 1
        return context

"""
Class-based CreateView for creating a post on the discussion board.
"""
class CreatePostView(CreateView):
    model = Post
    template_name = 'restaurant/make_post.html'
    # Sets the form's fields according to the Post model
    fields = ['subject', 'body']

    # Redirects the user back to the discussion board upon a successful post.
    def get_success_url(self):
        return reverse('discussion_board')

    # Overrides the form_valid() function
    def form_valid(self, form):
        body, taboo_words_1 = filter_taboo_words(form.instance.body)
        subject, taboo_words_2 = filter_taboo_words(form.instance.subject)

        # Concatenate the lists of taboo words in the post subject and body.
        taboo_words = taboo_words_1 + taboo_words_2

        # Checks the number of taboo words.
        if taboo_words > 0:
            # A user receives a warning for using at least one taboo word
            Customer.objects.get(pk=self.request.user).inc_warning()

            # If there are more than 3 taboo words, the post is not sent to the discussion board,
            # the customer is redirected back to the discussion board, and is notified that their
            # post contains too many taboo words.
            if taboo_words > 3:
                messages.error(self.request, "Your post has too many taboo words.")
                return redirect(reverse('discussion_board'))

            messages.warning(self.request, "Your post has some taboo words. You have been warned.")

        form.instance.subject = subject
        form.instance.body = body
        form.instance.author = Customer.objects.get(pk=self.request.user)
        messages.success(self.request, "Your post has been added!")
        return super().form_valid(form)

"""
Class-based ListView of all menu items to be displayed on restaurant/menu.
"""
class MenuListView(ListView):
    model = Dish
    template_name = 'restaurant/menu.html'
    # Order the dishes by their tag value
    ordering = ['tag']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sorted_dishes = []
        cart = []
        user = self.request.user
        # Check if user is authenticated, if not show defautls
        if user.is_authenticated and Customer.is_customer(user):
            cust = Customer.get_customer(user)
            for item in cust.menuitems_set.all():
                cart.append({'item': item.item.name,
                'price': item.quantity * item.item.price,
                'quantity': item.quantity,
                'tag': item.item.tag,
                'dish_id': item.item.pk})
            context['cart'] = cart
            context['is_VIP'] = cust.is_VIP

        # If a customer has more than 3 orders, then we retrieve the customers top 3
        # ordered tags and return the highest rating of each tag category to be featured
        if user.is_authenticated and Customer.is_customer(user) and (len(user.customer.orders_set.all()) >= 3):
            cust = Customer.get_customer(user)

            dish_ids = [*map(lambda x: x['dishes'], Orders.objects.filter(customer = cust).values('dishes'))]
            dishes = [*map(lambda x: Dish.objects.get(pk=x), dish_ids)]
            tag_frequencies = {}
            for tag in TAG_CHOICES:
                tag_frequencies[tag[0]] = 0
            for dish in dishes:
                tag_frequencies[dish.tag] += 1

            # get the most frequent tag and pop it
            def getpop():
                tag = max(tag_frequencies, key=tag_frequencies.get)
                tag_frequencies.pop(tag)
                return tag

            highest_3_tags = [getpop() for i in range(3)]

            featured_dishes = [*map(lambda x: Dish.objects.filter(tag=x).order_by('-avg_ratings').first(), highest_3_tags)]
            sorted_dishes.append(('Featured', [featured_dishes]))
        else:
            top_3_ordered = Dish.objects.all().order_by('-num_of_orders')[0:3]
            top_3_rated = Dish.objects.all().order_by('-avg_ratings')[0:3]

            sorted_dishes.append(('Featured', [list(top_3_ordered), list(top_3_rated)]))

        # Iterates through the TAG_CHOICES to create lists of length 3 for the carousel slides in the HTML file
        # Note: The carousel is currently not working, so the menu items are simply displayed in rows of three
        # dishes.
        for tag in TAG_CHOICES:
            dish_tag_list = Dish.objects.filter(tag=tag[0])
            # We want 3 items per slide
            n = 3
            divided_list = [dish_tag_list[i:i + n] for i in range(0, len(dish_tag_list), n)]
            sorted_dishes.append((tag[1], divided_list))

        context['sorted_dishes'] = sorted_dishes
        return context

"""
Class-based DetailView for each dish. Pages URLs are of form /restaurant/menu/<int:pk> as described
in restaurant/views.py.
"""
class MenuDetailView(DetailView):
    model = Dish
    context_object_name = 'dish'

"""
Class-based CreateView for ratings.
"""
class RateCreateView(CreateView):
    model = Rating
    template_name = 'restaurant/rate.html'
    fields = ['rating']

    # Redirect back to the menu after successfully rating a dish
    def get_success_url(self):
        return reverse('menu')

    # Override get_context_data() so the form for restaurant/rate.html to have access to the dishes
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dish'] = Dish.objects.get(pk=self.kwargs['pk'])
        return context

    # Override form_valid()
    # Dish ratings are updated here. VIP ratings are counted twice.
    def form_valid(self, form):
        cust = Customer.objects.get(pk=self.request.user.id)
        rating = form.instance.rating
        form.instance.dish = Dish.objects.get(pk=self.kwargs['pk'])
        total_ratings = form.instance.dish.total_ratings
        avg_ratings = form.instance.dish.avg_ratings
        if cust.is_VIP:
            form.instance.dish.total_ratings = total_ratings + 2
            form.instance.dish.avg_ratings = (2*rating + avg_ratings*total_ratings) / form.instance.dish.total_ratings
        else:
            form.instance.dish.total_ratings = total_ratings + 1
            form.instance.dish.avg_ratings = (rating + avg_ratings*total_ratings) / form.instance.dish.total_ratings
        print(form.instance.dish.avg_ratings)
        form.instance.dish.save()
        messages.success(self.request, 'Your rating has been added!')
        return super().form_valid(form)

"""
Function-based view for adding to cart. This is called every time the "Add to Cart" button is pressed.
The user is just redirected back to the menu page with the updated cart.
"""
@login_required
def add_to_cart(request):
    #On Windows, this function may give WinError10053, but it still works.
    print("On Windows, this function may give WinError10053, but it still works.")
    if request.method == 'POST':
        cust = Customer.objects.get(pk=request.user.id)
        # index 0 to just grab the Cart object instead of the tuple of (Cart, Boolean)
        cart = cust.menuitems_set
        dish_id = request.POST.get('dish_id')
        quantity = request.POST.get('quantity')
        print(dish_id)
        item = Dish.objects.get(pk=dish_id)
        menu_item = cart.all().filter(item=item).first()
        if not menu_item:
            menu_item = cart.create(item=item, quantity=quantity)
        else:
            menu_item.quantity = F('quantity') + quantity
        menu_item.save()
        return redirect('menu')

"""
Function-based view for removing to cart. This is called every time the "Remove from Cart" option is pressed.
The user is just redirected back to the menu page with the updated cart.
"""
@login_required
def remove_from_cart(request):
    """
    On Windows, this function may give WinError10053, but it still works. Don't worry sm:)e.
    """
    print("On Windows, this function may give WinError10053, but it still works. Don't worry sm:)e.")
    if request.method == 'POST':
        cust = Customer.objects.get(pk=request.user.id)
        # index 0 to just grab the Cart object instead of the tuple of (Cart, Boolean)
        cart = cust.menuitems_set
        dish_id = request.POST.get('dish_id')
        item = Dish.objects.get(pk=dish_id)
        cart.all().filter(item=item).first().delete()
        return redirect('menu')

"""
Function view for checkout.
"""
@login_required
def checkout(request):
    return render(request, 'restaurant/checkout.html')

"""
Function-based used to create an order when the takeout option is selected since takeout is a function-based
view.
"""
def create_order(**kwargs):
    order = Orders(
                customer = kwargs['customer'],
                chef_prepared = kwargs['chef_prepared'],
                cost = kwargs['cost'],
                dining_option = 'P')
    order.save()
    return order

"""
Takeout function-based view for when a customer chooses to order takeout. When the order is placed, the
customer's balance is updated. If the customer is a VIP, they get a 10% discount.
"""
@login_required
def takeout(request):
    if request.method == 'GET':
        return render(request, 'restaurant/takeout.html')
    elif request.method == 'POST':
        cust = Customer.objects.get(pk=request.user.id)
        chefs = Chef.objects.all()
        chef_prepared = chefs[randrange(len(chefs))]
        cost = cust.get_cart_price()
        menu_items = cust.menuitems_set.all()

        # Updates the last_ordered_date for a given Dish related to the MenuItem
        for item in menu_items:
            item.update_item_date()
        print('TAKEOUT WORKS')
        order = create_order(
            customer = cust,
            chef_prepared = chef_prepared,
            cost = cost,
            dining_option = 'P'
        )

        order.dishes.add(*list(map(lambda x: x['item'], menu_items.values('item'))))
        order.save()

        # Checks if the customer is a VIP to see if a discount needs to be applied
        if cust.is_VIP:
            cust.balance = F('balance') - cost * Decimal(0.9)
        else:
            cust.balance = F('balance') - cost
        cust.save()
        cust.check_vip()
        ### cust.menuitems_set.all().delete()
        return redirect(reverse('order_success'))

"""
Class-based CreateView for when the customer picks their dining option as "Delivery."
"""
class DeliveryCreateView(CreateView):
    model = Orders
    template_name = 'restaurant/delivery.html'
    fields = ['delivery_address']

    # Set the redirect page upon a successful order to restaurant/order_success
    def get_success_url(self):
        return reverse('order_success')

    # Override the form_valid() function.
    def form_valid(self, form):
        cust = Customer.objects.get(pk=self.request.user.id)
        form.instance.customer = cust

        chefs = Chef.objects.all()
        dps = DeliveryPerson.objects.all()

        form.instance.chef_prepared = chefs[randrange(len(chefs))]
        form.instance.cost = cust.get_cart_price()
        form.instance.delivery_person = dps[randrange(len(dps))]

        form.save()

        # Updates the last_ordered_date for a given Dish related to the MenuItem
        menu_items = cust.menuitems_set.all()
        form.instance.dishes.add(*list(map(lambda x: x['item'], menu_items.values('item'))))
        for item in cust.menuitems_set.all():
            item.update_item_date()

        cost = form.instance.cost
        ### delete the active order (MenuItem) here

        #### cust.menuitems_set.all().delete()

        # Checks if the customer is a VIP to see if a discount needs to be applied
        if cust.is_VIP:
            cust.balance = F('balance') - cost * Decimal(0.9)
        else:
            cust.balance = F('balance') - cost
        cust.save()
        cust.check_vip()
        return super().form_valid(form)

class DateInputWidget(DateInput):
    input_type = 'date'

"""
Class-based CreateView for when the customer picks their dining option as "Dine In."
"""
class DineInCreateView(CreateView):
    model = Orders
    template_name = 'restaurant/dinein.html'
    fields = ['dine_in_time']

    # Set the redirect page upon a successful order to restaurant/order_success
    def get_success_url(self):
        return reverse('order_success')

    # Override the form_valid() function.
    def form_valid(self, form):
        cust = Customer.objects.get(pk=self.request.user.id)
        form.instance.customer = cust
        chefs = Chef.objects.all()
        form.instance.chef_prepared = chefs[randrange(len(chefs))]
        form.instance.cost = cust.get_cart_price()
        for item in cust.menuitems_set.all():
            item.update_item_date()
        ### delete the active order (MenuItem) here
        form.save()

        # Updates the last_ordered_date for a given Dish related to the MenuItem
        menu_items = cust.menuitems_set.all()
        form.instance.dishes.add(*list(map(lambda x: x['item'], menu_items.values('item'))))
        for item in cust.menuitems_set.all():
            item.update_item_date()

        cost = form.instance.cost

        # Checks if the customer is a VIP to see if a discount needs to be applied
        if cust.is_VIP:
            cust.balance = F('balance') - cost * Decimal(0.9)
        else:
            cust.balance = F('balance') - cost
        cust.save()
        cust.check_vip()
        return super().form_valid(form)

    class Meta:
        widgets = {'dine_in_time': DateInputWidget()}

"""
Function-based view for the order success page. Users will be redirected here upon completion of their order.
"""
@login_required
def order_success(request):
    context = {'uuid': uuid4()}
    return render(request, 'restaurant/order_success.html', context=context)

"""
Function-based view for user-registration.
"""
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.instance.is_active = False
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Your account has been created! Please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'restaurant/register.html', {'form': form})

"""
Function-based view for a user's personal profile page.
"""
@login_required
def profile(request):
    # Checks a user's warning count to output a Django flash message corresponding to the number of warnings.
    if Customer.is_customer(request.user):
        cust = Customer.objects.filter(pk=request.user.id).first()
        if cust.warnings == 2:
            messages.error(request, 'YOU HAVE 2 WARNINGS. ONE MORE WARNING WILL GET YOU REMOVED FROM THE SITE.')
        elif cust.warnings == 1:
            messages.warning(request, 'You have 1 warning. Be careful!')
        elif cust.warnings == 0:
            messages.info(request, 'You have 0 warnings. Keep it up!')
        elif cust.warnings < 0:
            messages.success(request, 'You have ' + str(-1*cust.warnings) + ' compliment(s). Nice job!')

        reports = Report.objects.filter(complainee=request.user.id)
        m = 0
        for report in reports:
            if not report.is_disputed:
                m += 1
        if m > 0:
            messages.warning(request, 'You have ' + str(m) + ' report(s) against you. Please click "Dispute Complaints or Reports" if you wish to dispute.')

        complaints = Complaints.objects.filter(recipient=request.user.id)
        n = 0
        for complaint in complaints:
            if not complaint.is_disputed:
                n += 1
        if n > 0:
            messages.warning(request, 'You have ' + str(n) + ' complaint(s) against you. Please click "Dispute Complaints or Reports" if you wish to dispute.')
    return render(request, 'restaurant/profile.html')

"""
Class-based CreateView for when a customer files a report against another customer for misbehaving on the
discussion board.
"""
class CreateReportView(CreateView):
    model = Report
    template_name = 'restaurant/report.html'
    fields = ['report_body']

    # Override the context so that the original post's author can be seen in the report.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Customer.objects.get(pk=self.kwargs['pk'])
        return context

    # Sends the user back to the discussion board upon successfully submitting the report.
    def get_success_url(self):
        return reverse('discussion_board')

    # Overrides the form_valid() function
    def form_valid(self, form):
        form.instance.snitch = Customer.objects.get(pk=self.request.user.id)
        form.instance.complainee = Customer.objects.get(pk=self.kwargs['pk'])
        messages.success(self.request, "Your report has been received!")
        return super().form_valid(form)

"""
Class-based ListView for when a customer chooses to view reports made against them.
"""
class DisputeListView(ListView):
    model = Report
    template_name = 'restaurant/dispute_list.html'
    #context_object_name = 'reports'
    # Sort unprocessed reports by time reported with the most recent report being the first one.
    ordering = ['-time_reported']

    # Override the get_context_data() function so that the DisputeListView has access to both reports
    # and complaints.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Customer.is_customer(self.request.user):
            context['reports'] = Report.objects.filter(complainee=self.request.user.id)
        context['complaints'] = Complaints.objects.filter(recipient=self.request.user)
        return context

"""
Class-based UpdateView for when a customer chooses to dispute a report made against them.
"""
class DisputeUpdateView(UpdateView):
    model = Report
    template_name = 'restaurant/dispute_form.html'
    fields = ['dispute_body']

    # Override the context so that the user sees who reported them.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['snitch'] = Report.objects.get(pk=self.kwargs['pk']).snitch
        return context

    # Redirect the user back to the discussion board after successfully submitting the dispute.
    def get_success_url(self):
        return reverse('discussion_board')

    # Override the form_valid() function.
    def form_valid(self, form):
        messages.success(self.request, "Your dispute has been received!")
        # Sets the is_disputed attribute to true for the manager to see.
        form.instance.is_disputed = True
        return super().form_valid(form)

"""
Class-based UpdateView for when a customer chooses to dispute a complaint made against them.
"""
class DisputeComplaintView(UpdateView):
    model = Complaints
    template_name = 'restaurant/dispute_complaint.html'
    fields = ['dispute_body']

    # Override the context so that the user sees who reported them.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sender'] = Complaints.objects.get(pk=self.kwargs['pk']).sender
        return context

    # Redirect the user back to the discussion board after successfully submitting the dispute.
    def get_success_url(self):
        return reverse('discussion_board')

    # Override the form_valid() function.
    def form_valid(self, form):
        messages.success(self.request, "Your dispute has been received!")
        # Sets the is_disputed attribute to true for the manager to see.
        form.instance.is_disputed = True
        return super().form_valid(form)
