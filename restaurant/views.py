from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, DepositForm#, PostForm
from django.contrib.auth.decorators import login_required
from .models import Customer, Post, Report, Dish, Orders, Chef, DeliveryPerson, TAG_CHOICES
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse
from django.db.models import F
from random import randrange
from uuid import uuid4
from django.forms import DateInput

TABOO_WORDS = ['fk', 'fu', 'shoit']

# Create your views here.
def index(request):
    #return HttpResponse('Welcome to the restaurant')
    return render(request, 'restaurant/index.html')

def about(request):
    return render(request, 'restaurant/about.html')
    #return HttpResponse('About Page')

@login_required
def complaint_compliment(request):
    return render(request, 'restaurant/complaint_compliment.html')

@login_required
def deposit(request):
    customer = Customer.objects.get(pk=request.user.id)
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            #customer.update(balance=customer.balance + form.cleaned_data.get('amount'))
            #customer.refresh_from_db()
            customer.balance = customer.balance + form.cleaned_data.get('amount')
            customer.save()
            customer.deposit_set.create(amount=customer.balance)
            messages.success(request, "The amount has been added to your balance!")
    else:
        form = DepositForm()
    # user's current balance goes here
    #print(Customers.objects.get(pk=request.user.id).balance)
    context = {
        'balance': customer.balance,
        'form': form
    }
    return render(request, 'restaurant/deposit.html', context)

'''def discussion_board(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'restaurant/discussion_board.html', context)'''

class DiscussionBoardView(ListView):
    model = Post
    template_name = 'restaurant/discussion_board.html'
    context_object_name = 'posts'
    ordering = ['-time_posted']

def home(request):
    return render(request, 'restaurant/main_page.html')

def login(request):
    return render(request, 'restaurant/login.html')

#make_post() was turned into a class-based view.
'''@login_required
def make_post(request):
    customer = Customer.objects.get(pk=request.user.id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your post has been created!")
            return redirect('discussion_board')
    else:
        form = PostForm()
    return render(request, 'restaurant/make_post.html', {'form': form})'''

class SpecificPostView(DetailView):
    model = Post
    context_object_name = 'post'

def filter_taboo_words(text):
    split_text = text.split()
    total_taboo_words = 0
    print('TEXT:', text, 'SPLIT', split_text)
    for i, word in enumerate(split_text):
        if word in TABOO_WORDS:
            split_text[i] = '***'
            total_taboo_words += 1

    return ' '.join(split_text), total_taboo_words

class CreatePostView(CreateView):
    model = Post
    template_name = 'restaurant/make_post.html'
    fields = ['subject', 'body']

    def get_success_url(self):
        return reverse('discussion_board')

    def form_valid(self, form):
        body, taboo_words_1 = filter_taboo_words(form.instance.body)
        subject, taboo_words_2 = filter_taboo_words(form.instance.subject)

        taboo_words = taboo_words_1 + taboo_words_2

        if taboo_words > 0:
            Customer.objects.get(pk=self.request.user).inc_warning()
            if taboo_words > 3:
                messages.error(self.request, "Your post has too many taboo words.")
                return redirect(reverse('discussion_board'))

            messages.warning(self.request, "Your post has some taboo words. You have been warned.")

        form.instance.subject = subject
        form.instance.body = body
        form.instance.author = Customer.objects.get(pk=self.request.user)
        messages.success(self.request, "Your post has been added!")
        return super().form_valid(form)

'''def menu(request):
    # user's personalized dishes go here
    # menu goes here
    return render(request, 'restaurant/menu.html')
'''

class MenuListView(ListView):
    model = Dish
    template_name = 'restaurant/menu.html'
    #context_object_name = 'dishes'
    ordering = ['tag']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sorted_dishes = []
        for tag in TAG_CHOICES:
            dish_tag_list = Dish.objects.filter(tag=tag[0])
            # We want 3 items per slide
            n = 3
            divided_list = [dish_tag_list[i:i + n] for i in range(0, len(dish_tag_list), n)]
            sorted_dishes.append((tag[1], divided_list))
        context['sorted_dishes'] = sorted_dishes
        cart = []
        # Check if user is authenticated, if not show defautls
        for item in Customer.get_customer(self.request.user).menuitems_set.all():
            cart.append({'item': item.item.name,
            'price': item.quantity * item.item.price,
            'quantity': item.quantity})
        context['cart'] = cart
        return context

@login_required
def add_to_cart(request):
    """
    On Windows, this function may give WinError10053, but it still works. Don't worry sm:)e.
    """
    print("On Windows, this function may give WinError10053, but it still works. Don't worry sm:)e.")
    if request.method == 'POST':
        cust = Customer.objects.get(pk=request.user)
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

"""@login_required
def remove_from_cart(request, dish_id):"""

@login_required
def checkout(request):
    return render(request, 'restaurant/checkout.html')

# Temporary Views for Forms
@login_required
def delivery(request):
    return render(request, 'restaurant/delivery.html')

@login_required
def dinein(request):
    return render(request, 'restaurant/dinein.html')

@login_required
def takeout(request):
    if request.method == 'GET':
        return render(request, 'restaurant/takeout.html')
    elif request.method == 'POST':
        cust = Customer.objects.get(pk=request.user.id)
        chefs = Chef.objects.all()
        chef_prepared = chefs[randrange(len(chefs))]
        cost = cust.get_cart_price()
        for item in cust.menuitems_set.all():
            item.update_item_date()
        print('TAKEOUT WORKS')    
        Orders(
            customer = cust,
            chef_prepared = chef_prepared,
            cost = cost,
            dining_option = 'P'
        ).save()
        return redirect(reverse('order_success'))

class DeliveryCreateView(CreateView):
    model = Orders
    template_name = 'restaurant/delivery.html'
    fields = ['delivery_address']

    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Post.objects.get(pk=self.kwargs['pk']).author
        return context"""

    def get_success_url(self):
        return reverse('order_success')

    def form_valid(self, form):
        cust = Customer.objects.get(pk=self.request.user.id)
        form.instance.customer = cust
        chefs = Chef.objects.all()
        dps = DeliveryPerson.objects.all()
        form.instance.chef_prepared = chefs[randrange(len(chefs))]
        form.instance.cost = cust.get_cart_price()
        form.instance.delivery_person = dps[randrange(len(dps))]
        for item in cust.menuitems_set.all():
            item.update_item_date()
        # delete the active order (MenuItem) here
        # cust.menuitems_set.all().delete()
        return super().form_valid(form)

class DateInputWidget(DateInput):
    input_type = 'date'

class DineInCreateView(CreateView):
    model = Orders
    template_name = 'restaurant/dinein.html'
    fields = ['dine_in_time']

    def get_success_url(self):
        return reverse('order_success')

    def form_valid(self, form):
        cust = Customer.objects.get(pk=self.request.user.id)
        form.instance.customer = cust
        chefs = Chef.objects.all()
        form.instance.chef_prepared = chefs[randrange(len(chefs))]
        form.instance.cost = cust.get_cart_price()
        for item in cust.menuitems_set.all():
            item.update_item_date()        
        # delete the active order (MenuItem) here
        return super().form_valid(form)

    class Meta:
        widgets = {'dine_in_time': DateInputWidget()}

# class TakeoutCreateView(CreateView):
#     model = Orders
#     template_name = 'restaurant/takeout.html'
#     fields = ['']

#     def get_success_url(self):
#         return reverse('order_success')

#     def form_valid(self, form):
        
#         # delete the active order (MenuItem) here
#         return super().form_valid(form)

@login_required
def order_success(request):
    context = {'uuid': uuid4()}
    return render(request, 'restaurant/order_success.html', context=context)

# This one
"""class OrderCreateView(CreateView):
    model = Order
    template_name = 'restaurant/checkout.html'
    fields = ['']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Post.objects.get(pk=self.kwargs['pk']).author
        return context

    def get_success_url(self):
        return reverse('discussion_board')

    def form_valid(self, form):
        #Add a check for user == author
        form.instance.snitch = Customer.objects.get(pk=self.request.user.id)
        form.instance.complainee = Customer.objects.get(pk=Post.objects.get(pk=self.kwargs['pk']).author)
        messages.success(self.request, "Your report has been received!")
        return super().form_valid(form)"""


"""class MenuUpdateView(UpdateView):
    model = Order

    def get(self, request):
        if self.kwargs['pk']:"""

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Your account has been created! Please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'restaurant/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'restaurant/profile.html')

'''@login_required
def report(request):
    return render(request, 'restaurant/report.html')'''

class CreateReportView(CreateView):
    model = Report
    template_name = 'restaurant/report.html'
    fields = ['report_body']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Post.objects.get(pk=self.kwargs['pk']).author
        return context

    def get_success_url(self):
        return reverse('discussion_board')

    def form_valid(self, form):
        #Add a check for user == author
        form.instance.snitch = Customer.objects.get(pk=self.request.user.id)
        form.instance.complainee = Customer.objects.get(pk=Post.objects.get(pk=self.kwargs['pk']).author)
        messages.success(self.request, "Your report has been received!")
        return super().form_valid(form)

class DisputeListView(ListView):
    model = Report
    template_name = 'restaurant/dispute_list.html'
    context_object_name = 'reports'
    ordering = ['-time_reported']

    def get_queryset(self):
        return Report.objects.filter(complainee=self.request.user.id)

class DisputeUpdateView(UpdateView):
    model = Report
    template_name = 'restaurant/dispute_form.html'
    fields = ['dispute_body']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['snitch'] = Report.objects.get(pk=self.kwargs['pk']).snitch
        return context

    def get_success_url(self):
        return reverse('discussion_board')

    def form_valid(self, form):
        messages.success(self.request, "Your dispute has been received!")
        form.instance.is_disputed = True
        return super().form_valid(form)

'''@login_required
def dispute(request):
    return render(request, 'restaurant/dispute.html')'''
