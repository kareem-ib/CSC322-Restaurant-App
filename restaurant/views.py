from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, DepositForm#, PostForm
from django.contrib.auth.decorators import login_required
from .models import Customer, Post, Report
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse

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
            customer.deposits_set.create(amount=customer.balance)
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

class CreatePostView(CreateView):
    model = Post
    template_name = 'restaurant/make_post.html'
    fields = ['subject', 'body']

    def get_success_url(self):
        return reverse('discussion_board')

    def form_valid(self, form):
        form.instance.author = Customer.objects.get(pk=self.request.user.id)
        messages.success(self.request, "Your post has been added!")
        return super().form_valid(form)

def menu(request):
    # user's personalized dishes go here
    # menu goes here
    return render(request, 'restaurant/menu.html')

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
        form.instance.snitch = Customer.objects.get(pk=self.request.user.id)
        form.instance.complainee = Customer.objects.get(pk=Post.objects.get(pk=self.kwargs['pk']).author)
        messages.success(request, "Your report has been received!")
        return super().form_valid(form)

@login_required
def dispute(request):
    return render(request, 'restaurant/dispute.html')
