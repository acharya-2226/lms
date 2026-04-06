from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class FirstLoginPasswordChangeForm(forms.Form):
    """Form for changing password on first login"""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password',
        }),
        help_text='Enter the temporary password provided to you'
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a new password',
            'autocomplete': 'new-password',
        }),
        help_text='Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.'
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password',
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_old_password(self):
        """Validate old password"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('The old password is incorrect.')
        return old_password
    
    def clean_new_password1(self):
        """Validate new password strength"""
        new_password1 = self.cleaned_data.get('new_password1')
        
        if len(new_password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if not any(char.isupper() for char in new_password1):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not any(char.islower() for char in new_password1):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not any(char.isdigit() for char in new_password1):
            raise ValidationError('Password must contain at least one digit.')
        
        return new_password1
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('The two passwords do not match.')
        
        return cleaned_data
    
    def save(self):
        """Save the new password"""
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user
