from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from restaurant import views as user_views
from .views import (DiscussionBoardView, 
SpecificPostView, 
CreatePostView, 
CreateReportView, 
DisputeListView, 
DisputeUpdateView)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('complaint_compliment/', views.complaint_compliment, name='complaint_compliment'),
    path('deposit/', views.deposit, name='deposit'),
    #path('discussion_board/', views.discussion_board, name='discussion_board'),
    path('discussion_board/', DiscussionBoardView.as_view(), name='discussion_board'),
    path('discussion_board/post/<int:pk>/', SpecificPostView.as_view(), name='post_detail'),
    path('home/', views.home, name='home'),
    #path('make_post/', views.make_post, name='make_post'),
    path('make_post/', login_required(CreatePostView.as_view()), name='make_post'),
    path('menu/', views.menu, name='menu'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='restaurant/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('report/<int:pk>', login_required(CreateReportView.as_view()), name='report'),
    path('report/', login_required(CreateReportView.as_view()), name='report'),
    path('dispute/', login_required(DisputeListView.as_view()), name='dispute'),
    path('dispute/<int:pk>', login_required(DisputeUpdateView.as_view()), name='dispute'),
]
