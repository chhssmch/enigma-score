from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Profile
from .forms import CustomRegisterForm, ProfileForm


def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            profile = Profile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                birth_date=form.cleaned_data['birth_date'],
                monthly_income=form.cleaned_data['monthly_income'],
                employment_length=form.cleaned_data['employment_length']
            )
            
            login(request, user)
            return redirect('credit_score:home')
    else:
        form = CustomRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    user_profile = request.user.profile 
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=user_profile)
    
    from credit_score.models import CreditApplication
    credit_applications = CreditApplication.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': user_profile,
        'form': form,
        'credit_applications': credit_applications
    }
    return render(request, 'users/profile.html', context)

@login_required
def clear_history(request):
    if request.method == 'POST':
        try:
            from credit_score.models import CreditApplication
            deleted_count = CreditApplication.objects.filter(user=request.user).delete()[0]
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Deleted {deleted_count} credit applications from database.'
                })
            else:
                messages.success(request, f'Deleted {deleted_count} credit applications from database.')
                return redirect('users:profile')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error deleting applications: {str(e)}'
                })
            else:
                messages.error(request, f'Error deleting applications: {str(e)}')
                return redirect('users:profile')
    
    return redirect('users:profile')
