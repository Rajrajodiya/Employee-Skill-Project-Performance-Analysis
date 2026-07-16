"""Authentication views — single responsibility: user registration and login."""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.template import Template, Context
from django.urls import reverse

from apps.esppa.forms import UserRegistrationForm

logger = logging.getLogger(__name__)

# ── Login template (inline — no file dependency) ───────────────────────────
_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In — ESPPA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link rel="stylesheet" href="/static/style.css">
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <style>
        body { font-family: 'SF Pro Text', 'Inter', system-ui, -apple-system, sans-serif; font-size: 17px; line-height: 1.47; color: #1d1d1f; background: #f5f5f7; -webkit-font-smoothing: antialiased; }
        .font-display { font-family: 'SF Pro Display', system-ui, -apple-system, sans-serif; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center bg-[#f5f5f7]">
    <div class="w-full max-w-sm px-4">
        <!-- Brand -->
        <div class="text-center mb-10">
            <div class="w-14 h-14 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="fas fa-chart-line text-lg text-white"></i>
            </div>
            <h1 class="font-display text-3xl font-semibold text-[#1d1d1f]">ESPPA</h1>
            <p class="text-sm text-[#7a7a7a] mt-1">Employee Skill &amp; Performance Analyzer</p>
        </div>

        <!-- Card -->
        <div class="bg-white rounded-xl border border-gray-200/80 p-7">
            <h2 class="font-display text-xl font-semibold mb-1">Welcome back</h2>
            <p class="text-sm text-[#7a7a7a] mb-6">Sign in to your account</p>

            <form method="post" novalidate>
                {% csrf_token %}

                {% if form.errors %}
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-5 text-sm text-red-700 flex items-start gap-2">
                    <i class="fas fa-exclamation-circle mt-0.5"></i>
                    <span>Invalid username or password. Please try again.</span>
                </div>
                {% endif %}

                <div class="mb-4">
                    <label class="block text-xs font-medium text-[#1d1d1f] mb-1.5 tracking-wide uppercase">Username</label>
                    <input type="text" name="username" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#0066cc]/30 focus:border-[#0066cc] transition-all" placeholder="Enter your username" required>
                </div>

                <div class="mb-6">
                    <label class="block text-xs font-medium text-[#1d1d1f] mb-1.5 tracking-wide uppercase">Password</label>
                    <input type="password" name="password" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#0066cc]/30 focus:border-[#0066cc] transition-all" placeholder="Enter your password" required>
                </div>

                <button type="submit" class="w-full bg-[#0066cc] text-white text-base font-normal rounded-[9999px] px-5 py-2.5 hover:bg-[#0071e3] active:scale-[0.97] transition-all duration-150 cursor-pointer">
                    <i class="fas fa-arrow-right mr-2"></i>Sign In
                </button>
            </form>

            <p class="text-center text-sm text-[#7a7a7a] mt-6">
                Don't have an account?
                <a href="/register/" class="text-[#0066cc] hover:text-[#0071e3] transition-colors font-medium no-underline">
                    Register <i class="fas fa-arrow-right text-xs ml-0.5"></i>
                </a>
            </p>
        </div>

        <!-- Features -->
        <div class="mt-8 grid grid-cols-3 gap-4 text-center">
            <div><i class="fas fa-chart-bar text-[#0066cc] text-lg mb-1"></i><p class="text-[11px] text-[#7a7a7a] leading-tight">Advanced Analytics</p></div>
            <div><i class="fas fa-bolt text-[#0066cc] text-lg mb-1"></i><p class="text-[11px] text-[#7a7a7a] leading-tight">AI Predictions</p></div>
            <div><i class="fas fa-brain text-[#0066cc] text-lg mb-1"></i><p class="text-[11px] text-[#7a7a7a] leading-tight">Model Insights</p></div>
        </div>
    </div>
</body>
</html>
"""


def login_view(request):
    """
    Custom login view that renders from an inline template string.
    Bypasses Django template file loading to avoid Vercel bundling issues.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        # Form invalid — re-render with errors
    else:
        form = AuthenticationForm(request)

    template = Template(_LOGIN_TEMPLATE)
    context = Context({'form': form})
    rendered = template.render(context)
    return HttpResponse(rendered)


def register_view(request):
    """User registration view. Early return for GET."""
    if request.method != 'POST':
        return render(request, 'esppa/register.html', {'form': UserRegistrationForm()})

    form = UserRegistrationForm(request.POST)
    if not form.is_valid():
        return render(request, 'esppa/register.html', {'form': form})

    user = form.save()
    login(request, user)
    messages.success(request, 'Registration successful! Welcome to ESPPA.')
    return redirect('dashboard')
