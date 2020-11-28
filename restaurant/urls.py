from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('complaint_compliment/', views.complaint_compliment, name='complaint_compliment'),
    path('deposit/', views.deposit, name='deposit'),
    path('discussion_board/', views.discussion_board, name='discussion_board'),
    path('home/', views.home, name='home'),
    path('make_post/', views.make_post, name='make_post'),
    path('menu/', views.menu, name='menu'),
    path('register/', views.register, name='register')
]
