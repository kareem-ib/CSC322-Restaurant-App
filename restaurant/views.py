from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required

posts = [
    {
        'author': 'Author 1',
        'title': 'Exam 2 Comments',
        'content': 'Trash exams. Drop the course.',
        'date_posted': 'November 25, 2020'
    },
    {
        'author': 'Author 2',
        'title': 'Update to Project',
        'content': 'Project is cancelled. You all get 0s.',
        'date_posted': 'November 25, 2020'
    }
]

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
    # user's current balance goes here
    return render(request, 'restaurant/deposit.html')

def discussion_board(request):
    context = {
        'posts': posts
    }
    return render(request, 'restaurant/discussion_board.html', context)

def home(request):
    return render(request, 'restaurant/main_page.html')

def login(request):
    return render(request, 'restaurant/login.html')

@login_required
def make_post(request):
    return render(request, 'restaurant/make_post.html')

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

@login_required
def report(request):
    return render(request, 'restaurant/report.html')

@login_required
def dispute(request):
    return render(request, 'restaurant/dispute.html')
