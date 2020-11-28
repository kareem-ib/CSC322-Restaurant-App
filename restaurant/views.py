from django.shortcuts import render
from django.http import HttpResponse

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

def complaint_compliment(request):
    return render(request, 'restaurant/complaint_compliment.html')

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

def make_post(request):
    return render(request, 'restaurant/make_post.html')

def menu(request):
    # user's personalized dishes go here
    # menu goes here
    return render(request, 'restaurant/menu.html')

def register(request):
    return render(request, 'restaurant/register.html')
