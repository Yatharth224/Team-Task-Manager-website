from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.MeView.as_view(), name='me'),
    path('sessions/', views.ActiveSessionsView.as_view(), name='active-sessions'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]