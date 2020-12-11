from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, DepositForm, ComplimentForm, ComplaintForm, RatingForm
from django.contrib.auth.decorators import login_required
from .models import User, Customer, Post, Report, Dish, Orders, Chef, DeliveryPerson, Compliments, Complaints, Rating, TAG_CHOICES
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.urls import reverse
from django.db.models import F
from random import randrange
from uuid import uuid4
from django.forms import DateInput
from django import forms

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

class ComplimentCreateView(FormView):
    model = Compliments
    template_name = 'restaurant/compliment.html'
    #fields = ['recipient', 'body']
    form_class = ComplimentForm

    def get_success_url(self):
        return reverse('home')

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

    def form_valid(self, form):
        print("form valid")
        self.request.user.compliments_sender.create(recipient=User.objects.get(pk=form.cleaned_data.get('recipient')),
                                                    body=form.cleaned_data.get('body'))

        messages.success(self.request, "Your compliment has been received!")
        return super().form_valid(form)

class ComplaintCreateView(FormView):
    model = Complaints
    template_name = 'restaurant/complaint.html'
    #fields = ['recipient', 'body']
    form_class = ComplaintForm

    def get_success_url(self):
        return reverse('home')

    def get_form_kwargs(self):
        kwargs = super(ComplaintCreateView, self).get_form_kwargs()
        user = self.request.user
        cust = user.customer
        orders = cust.orders_set.all()
        lst = []
        for order in orders:
            lst.append((order.chef_prepared.user_ptr.pk, order.chef_prepared.get_full_name()))
            if order.delivery_person:
                lst.append((order.delivery_person.user_ptr.pk, order.delivery_person.get_full_name()))
        lst = tuple(dict.fromkeys(lst))
        kwargs['choices'] = lst
        return kwargs

    def form_valid(self, form):
        print("form valid")
        self.request.user.complaints_sender.create(recipient=User.objects.get(pk=form.cleaned_data.get('recipient')),
                                                   complaint_body=form.cleaned_data.get('complaint_body'))

        messages.success(self.request, "Your complaint has been received!")
        return super().form_valid(form)

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
            print(form.fields)
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

class MenuListView(ListView):
    model = Dish
    template_name = 'restaurant/menu.html'
    #context_object_name = 'dishes'
    ordering = ['tag']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sorted_dishes = []
        cart = []
        # Check if user is authenticated, if not show defautls
        if self.request.user.is_authenticated:
            cust = Customer.get_customer(self.request.user)
            for item in cust.menuitems_set.all():
                cart.append({'item': item.item.name,
                'price': item.quantity * item.item.price,
                'quantity': item.quantity,
                'tag': item.item.tag})
            context['cart'] = cart
            context['is_VIP'] = cust.is_VIP
        else:
            top_3_ordered = Dish.objects.all().order_by('-num_of_orders')[0:3]
            top_3_rated = Dish.objects.all().order_by('-avg_ratings')[0:3]

            sorted_dishes.append(('Featured', [list(top_3_ordered), list(top_3_rated)]))

        for tag in TAG_CHOICES:
            dish_tag_list = Dish.objects.filter(tag=tag[0])
            # We want 3 items per slide
            n = 3
            divided_list = [dish_tag_list[i:i + n] for i in range(0, len(dish_tag_list), n)]
            sorted_dishes.append((tag[1], divided_list))

        context['sorted_dishes'] = sorted_dishes
        return context

class MenuDetailView(DetailView):
    model = Dish
    context_object_name = 'dish'

class RateCreateView(CreateView):
    """model = Dish
    template_name = 'restaurant/rate.html'
    form_class = RatingForm

    def get_success_url(self):
        return reverse('menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

    def form_valid(self, form):
        rating = DishForm.instance.rating
        form.instance.total_ratings = F('total_ratings') + 1
        form.instance.avg_ratings = (rating + F('avg_ratings')) / F('total_ratings')
        messages.success(self.request, 'Your rating has been added!')
        return super().form_valid(form)"""

    model = Rating
    template_name = 'restaurant/rate.html'
    fields = ['rating']

    def get_success_url(self):
        return reverse('menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dish'] = Dish.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        rating = form.instance.rating
        form.instance.dish = Dish.objects.get(pk=self.kwargs['pk'])
        total_ratings = form.instance.dish.total_ratings
        avg_ratings = form.instance.dish.avg_ratings
        form.instance.dish.total_ratings = total_ratings + 1
        form.instance.dish.avg_ratings = (rating + avg_ratings*total_ratings) / form.instance.dish.total_ratings
        print(form.instance.dish.avg_ratings)
        form.instance.dish.save()
        messages.success(self.request, 'Your rating has been added!')
        return super().form_valid(form)

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
        if cust.is_VIP:
            cust.balance = F('balance') - cost * 0.9
        else:
            cust.balance = F('balance') - cost
        cust.check_vip()
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
        if cust.is_VIP:
            cust.balance = F('balance') - cost * 0.9
        else:
            cust.balance = F('balance') - cost
        cust.check_vip()
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
        if cust.is_VIP:
            cust.balance = F('balance') - cost * 0.9
        else:
            cust.balance = F('balance') - cost
        cust.check_vip()
        return super().form_valid(form)

    class Meta:
        widgets = {'dine_in_time': DateInputWidget()}

@login_required
def order_success(request):
    context = {'uuid': uuid4()}
    return render(request, 'restaurant/order_success.html', context=context)

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
