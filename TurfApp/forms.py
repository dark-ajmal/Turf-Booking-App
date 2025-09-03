from django import forms
from .models import TurfUser, TurfVenue, Amenity
from django.contrib.auth.forms import PasswordChangeForm as AuthPasswordChangeForm

class UpdateProfileForm(forms.ModelForm):
    """
    A form for the owner to update their profile information.
    """
    class Meta:
        model = TurfUser
        fields = ['name', 'phone', 'profile_picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PasswordChangeForm(AuthPasswordChangeForm):
    """
    A secure form for the owner to change their password, inheriting from Django's built-in form
    for better security and session handling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter current password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter new password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})

class TurfVenueForm(forms.ModelForm):
    """
    A comprehensive form for creating and updating TurfVenue instances.
    """
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Standard Amenities"
    )

    class Meta:
        model = TurfVenue
        fields = [
            'name', 'location', 'sports_type', 'price_per_hour', 'image',
            'no_of_players', 'open_time', 'close_time', 'description',
            'google_maps_link', 'amenities', 'custom_amenities'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
            'google_maps_link': forms.URLInput(attrs={'placeholder': 'Paste Google Maps link here'}),
            # --- FIX: Changed TextInput to HiddenInput ---
            'custom_amenities': forms.HiddenInput(), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a consistent class to all form fields for styling
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

