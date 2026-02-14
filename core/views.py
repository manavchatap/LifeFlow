from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import DonationRequest, Inventory, DonorProfile
from .forms import DonorSignUpForm, HospitalSignUpForm, InventoryForm, RequestForm

def home(request):
    return render(request, 'core/home.html')

def register(request):
    return render(request, 'core/register.html')

def donor_register(request):
    if request.method == 'POST':
        form = DonorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = DonorSignUpForm()
    return render(request, 'core/register_form.html', {'form': form, 'type': 'Donor'})

def hospital_register(request):
    if request.method == 'POST':
        form = HospitalSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = HospitalSignUpForm()
    return render(request, 'core/register_form.html', {'form': form, 'type': 'Hospital'})

@login_required
def dashboard(request):
    user = request.user
    
    # 1. HOSPITAL DASHBOARD
    if user.is_hospital:
        hospital = user.hospital_profile
        inventory = Inventory.objects.filter(hospital=hospital)
        my_requests = DonationRequest.objects.filter(hospital=hospital, is_active=True)
        
        if request.method == 'POST':
            if 'update_inventory' in request.POST:
                i_form = InventoryForm(request.POST)
                if i_form.is_valid():
                    Inventory.objects.update_or_create(
                        hospital=hospital,
                        blood_group=i_form.cleaned_data['blood_group'],
                        defaults={'unit_count': i_form.cleaned_data['unit_count']}
                    )
                    return redirect('dashboard')
            
            elif 'create_request' in request.POST:
                r_form = RequestForm(request.POST)
                if r_form.is_valid():
                    req = r_form.save(commit=False)
                    req.hospital = hospital
                    req.save()
                    
                    # EMAIL LOGIC
                    matching_donors = DonorProfile.objects.filter(
                        blood_group=req.blood_group,
                        city__iexact=hospital.city
                    )
                    recipient_list = [d.user.email for d in matching_donors if d.user.email]
                    
                    if recipient_list:
                        send_mail(
                            f"URGENT: {req.blood_group} Blood Needed",
                            f"Urgent request at {hospital.hospital_name} in {hospital.city}.",
                            settings.DEFAULT_FROM_EMAIL,
                            recipient_list,
                            fail_silently=True,
                        )
                    return redirect('dashboard')
        else:
            i_form = InventoryForm()
            r_form = RequestForm()
            
        return render(request, 'core/dashboard_hospital.html', {
            'inventory': inventory, 'my_requests': my_requests,
            'i_form': i_form, 'r_form': r_form
        })
    
    # 2. DONOR DASHBOARD
    elif user.is_donor:
        donor = user.donor_profile
        local_requests = DonationRequest.objects.filter(
            hospital__city__iexact=donor.city, 
            is_active=True
        ).order_by('-urgency')
        
        return render(request, 'core/dashboard_donor.html', {
            'requests': local_requests, 
            'donor': donor
        })
        
    return redirect('home')

def request_detail(request, pk):
    req = get_object_or_404(DonationRequest, pk=pk)
    return render(request, 'core/request_detail.html', {'req': req})

# --- NEW FUNCTION FOR BADGES ---
@login_required
def mark_donated(request):
    if hasattr(request.user, 'donor_profile'):
        donor = request.user.donor_profile
        donor.donation_count += 1
        donor.save()
    return redirect('dashboard')