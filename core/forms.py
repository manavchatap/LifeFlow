# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model # <--- KEY CHANGE 1
from django.db import transaction
from .models import DonorProfile, HospitalProfile, Inventory, DonationRequest

# Get the actual active User model (your custom core.User)
User = get_user_model() # <--- KEY CHANGE 2

# --- DONOR REGISTRATION ---
class DonorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required to receive donation alerts.")
    phone_number = forms.CharField(max_length=15, required=True)
    blood_group = forms.ChoiceField(choices=DonorProfile.BLOOD_CHOICES)
    city = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User # Now points to the CORRECT User model
        fields = ('username', 'email', 'phone_number',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_donor = True
        user.email = self.cleaned_data.get('email')
        # Check if your custom User model has a phone_number field
        if hasattr(user, 'phone_number'):
            user.phone_number = self.cleaned_data.get('phone_number')
        user.save()
        
        DonorProfile.objects.create(
            user=user,
            blood_group=self.cleaned_data.get('blood_group'),
            city=self.cleaned_data.get('city'),
            # If DonorProfile stores phone, uncomment below:
            # phone_number=self.cleaned_data.get('phone_number')
        )
        return user

# --- HOSPITAL REGISTRATION ---
class HospitalSignUpForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=200, required=True)
    city = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = User # Now points to the CORRECT User model
        fields = ('username', 'phone_number',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_hospital = True
        if hasattr(user, 'phone_number'):
            user.phone_number = self.cleaned_data.get('phone_number')
        user.save()
        
        HospitalProfile.objects.create(
            user=user,
            hospital_name=self.cleaned_data.get('hospital_name'),
            city=self.cleaned_data.get('city')
        )
        return user

# --- INVENTORY FORM ---
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['blood_group', 'unit_count']

# --- REQUEST FORM ---
class RequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ['blood_group', 'urgency']