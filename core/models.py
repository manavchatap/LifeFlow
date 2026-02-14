from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_hospital = models.BooleanField(default=False)
    is_donor = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    
    def __str__(self):
        return self.hospital_name

class DonorProfile(models.Model):
    BLOOD_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_CHOICES)
    city = models.CharField(max_length=100)
    last_donation_date = models.DateField(null=True, blank=True)
    donation_count = models.IntegerField(default=0)  # <--- NEW FIELD

    def __str__(self):
        return f"{self.user.username} ({self.blood_group})"

class Inventory(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=DonorProfile.BLOOD_CHOICES)
    unit_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class DonationRequest(models.Model):
    URGENCY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=DonorProfile.BLOOD_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)