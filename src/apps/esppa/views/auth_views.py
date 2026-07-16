"""Authentication views — single responsibility: user registration and login."""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from apps.esppa.forms import UserRegistrationForm

logger = logging.getLogger(__name__)


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
