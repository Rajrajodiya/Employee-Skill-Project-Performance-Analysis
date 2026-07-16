"""
Profile form — single responsibility: user profile editing.
"""

from django import forms

from apps.esppa.models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    class Meta:
        model = UserProfile
        fields = ['department', 'role', 'phone', 'profile_picture']
