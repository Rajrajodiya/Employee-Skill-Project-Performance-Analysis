"""
Authentication and Profile views for ESPPA.
"""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import UserProfile, Prediction, Analysis
from apps.esppa.forms import UserRegistrationForm, UserProfileForm

logger = logging.getLogger(__name__)


def register_view(request):
    """User registration view."""
    if request.method != 'POST':
        return render(request, 'esppa/register.html', {'form': UserRegistrationForm()})

    form = UserRegistrationForm(request.POST)
    if not form.is_valid():
        return render(request, 'esppa/register.html', {'form': form})

    user = form.save()
    login(request, user)
    messages.success(request, 'Registration successful! Welcome to ESPPA.')
    return redirect('dashboard')


@login_required
def profile_view(request):
    """User profile view and edit."""
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method != 'POST':
        return render(request, 'esppa/profile.html', {
            'form': UserProfileForm(instance=userprofile),
            'recent_predictions': Prediction.objects.filter(
                created_by=request.user).order_by('-created_at')[:10],
            'recent_analyses': Analysis.objects.filter(
                created_by=request.user).order_by('-created_at')[:10],
        })

    form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
    if not form.is_valid():
        return render(request, 'esppa/profile.html', {
            'form': form,
            'recent_predictions': Prediction.objects.filter(
                created_by=request.user).order_by('-created_at')[:10],
            'recent_analyses': Analysis.objects.filter(
                created_by=request.user).order_by('-created_at')[:10],
        })

    form.save()
    messages.success(request, 'Profile updated successfully!')
    return redirect('profile')
