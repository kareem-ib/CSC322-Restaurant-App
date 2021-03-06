from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from restaurant import views as user_views
from .views import (DiscussionBoardView,
                    SpecificPostView,
                    CreatePostView,
                    CreateReportView,
                    DisputeListView,
                    DisputeUpdateView,
                    DisputeComplaintView,
                    MenuListView,
                    MenuDetailView,
                    RateCreateView,
                    DeliveryCreateView,
                    DineInCreateView,
                    ComplaintCreateView,
                    ComplimentCreateView,
                    DPRateFormView,)
#                    TakeoutCreateView)

from . import views
#from ..restaurant_app import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('complain/', login_required(ComplaintCreateView.as_view()), name='complain'),
    path('compliment/', login_required(ComplimentCreateView.as_view()), name='compliment'),
    path('deposit/', views.deposit, name='deposit'),
    #path('discussion_board/', views.discussion_board, name='discussion_board'),
    path('discussion_board/', DiscussionBoardView.as_view(), name='discussion_board'),
    path('discussion_board/post/<int:pk>/', SpecificPostView.as_view(), name='post_detail'),
    path('home/', views.home, name='home'),
    #path('make_post/', views.make_post, name='make_post'),
    path('make_post/', login_required(CreatePostView.as_view()), name='make_post'),
    #path('menu/', views.menu, name='menu'),
    path('menu/', MenuListView.as_view(), name='menu'),
    path('menu/<int:pk>', MenuDetailView.as_view(), name='menu_detail'),
    path('menu/rate/<int:pk>', login_required(RateCreateView.as_view()), name='rate'),
    path('menu/add/', views.add_to_cart, name='add_to_cart'),
    path('menu/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('menu/search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/delivery', login_required(DeliveryCreateView.as_view()), name='delivery'),
    path('checkout/dinein', login_required(DineInCreateView.as_view()), name='dinein'),
    path('checkout/takeout', views.takeout, name='takeout'),
    path('order_success/', views.order_success, name='order_success'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='restaurant/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('report/<int:pk>', login_required(CreateReportView.as_view()), name='report'),
    path('report/', login_required(CreateReportView.as_view()), name='report'),
    path('dispute/', login_required(DisputeListView.as_view()), name='dispute'),
    path('dispute/report/<int:pk>', login_required(DisputeUpdateView.as_view()), name='dispute'),
    path('dispute/complaint/<int:pk>', login_required(DisputeComplaintView.as_view()), name='dispute_complaint'),
    path('apply/', views.apply, name='apply'),
    #path('apply/chef', CreateChefView.as_view(), name='apply_chef'),
    #path('apply/delivery_person', CreateDPView.as_view(), name='apply_dp'),
    path('apply/chef', views.apply_chef, name='apply_chef'),
    path('apply/delivery_person', views.apply_dp, name='apply_dp'),
    path('rate/delivery_person', login_required(DPRateFormView.as_view()), name='rate_dp'),
    path('quit/', views.quit_request, name='quit')
]

#urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
