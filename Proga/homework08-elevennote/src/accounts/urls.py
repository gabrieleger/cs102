from django.urls import include, path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import RegisterView, verify

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verify', verify, name='verify'),
    path('verify/<str:activation_code>', verify, name='verifycode'),
    path('register/', RegisterView.as_view(), name='register'),
]
