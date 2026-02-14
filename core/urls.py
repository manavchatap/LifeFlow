from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/donor/', views.donor_register, name='donor_register'),
    path('register/hospital/', views.hospital_register, name='hospital_register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    
    # --- NEW URL ---
    path('donated/', views.mark_donated, name='mark_donated'),
]