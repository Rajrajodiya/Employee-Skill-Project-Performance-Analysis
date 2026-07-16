"""Authentication views — single responsibility: user registration."""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from apps.esppa.forms import UserRegistrationForm

logger = logging.getLogger(__name__)


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to ESPPA.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'esppa/register.html', {'form': form})
