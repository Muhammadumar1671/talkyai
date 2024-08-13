from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('' , views.login_signup, name='login_signup'),
    path('logout/', views.logout_view, name='Logout'),
    path('is_valid_token/', views.is_valid_token, name='is_valid_token'),
]
