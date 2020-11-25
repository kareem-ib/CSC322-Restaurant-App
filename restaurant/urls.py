from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('discussion_board/', views.discussion_board, name='discussion_board')
]
