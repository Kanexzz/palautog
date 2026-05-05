from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages


class LoginView(View):
    """Handle user login."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')

        context = {
            'site_name': 'Faculty Scheduling System',
            'university_name': 'Carlos Hilado Memorial State University',
            'logo_text': 'CHMSU',
            'description': 'Faculty Scheduling System - Constraint-Based Optimization',
            'tagline': 'For University Departments - Optimize faculty scheduling using constraint-based algorithms for efficient resource allocation and conflict-free timetabling.',
        }
        return render(request, 'authentication/login.html', context)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            context = {
                'username': username,
                'site_name': 'Faculty Scheduling System',
                'university_name': 'Carlos Hilado Memorial State University',
                'logo_text': 'CHMSU',
            }
            return render(request, 'authentication/login.html', context)


class LogoutView(View):
    """Handle user logout."""

    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('index')
