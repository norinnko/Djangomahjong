from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm

class SignUpView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/register.html'

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

def logout_view(request):
    logout(request)
    return redirect('accounts:login')
