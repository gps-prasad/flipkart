from django.urls import path
from .views import *


urlpatterns = [
    path('register/',Register,name='register'),
    path('login/',Login,name='login'),
    path('logout/',Logout,name='logout'),
    path('dashboard/',Dashboard,name='dashboard'),
    path('',Dashboard,name='dashboard'),
    
    path('forgotpassword/',Forgotpassword,name='forgotpassword'),
    path('resetpassword/',Resetpassword,name='resetpassword'),
    
    path('activate/<uidb64>/<token>/',Activate,name='activate'),
    path('resetpassword_validate/<uidb64>/<token>/',Resetpassword_validate,name='resetpassword_validate'),
    path('my_orders/', my_orders, name='my_orders'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('change_password/', change_password, name='change_password'),
    path('order_details/<str:order_id>/', order_details, name='order_details'),
]