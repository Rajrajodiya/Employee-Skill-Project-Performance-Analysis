"""Profile views — single responsibility: user profile editing and display."""

import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import UserProfile, Prediction, Analysis
from apps.esppa.forms import UserProfileForm

logger = logging.getLogger(__name__)


@login_required
def profile_view(request):
    """User profile view and edit."""
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=userprofile)

    return render(request, 'esppa/profile.html', {
        'form': form,
        'recent_predictions': Prediction.objects.filter(
            created_by=request.user).order_by('-created_at')[:10],
        'recent_analyses': Analysis.objects.filter(
            created_by=request.user).order_by('-created_at')[:10],
    })
