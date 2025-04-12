from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import UserLoginActivity
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ContactForm, ProfileRegisterForm, EmailAuthenticationForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    
    def form_valid(self, form):
        # Call the parent class's form_valid method first
        response = super().form_valid(form)
        
        # Record the login activity
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            UserLoginActivity.objects.create(
                user=self.request.user,
                ip_address=self.request.META.get('REMOTE_ADDR')
            )
        
        return response


class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    http_method_names = ['get', 'post']  # Allow both GET and POST methods


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    from_email = settings.EMAIL_HOST_USER
    success_url = '/accounts/password-reset/done/'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Don't save profile form yet, just get the data
            profile = user.profile  # Profile is created via signal
            profile.institution_name = profile_form.cleaned_data.get('institution_name')
            profile.phone_number = profile_form.cleaned_data.get('phone_number')
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            
            username = user_form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()
    return render(request, 'accounts/register.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def user_list(request):
    # Only staff/admin can access this view
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    # Get all users ordered by last login date
    users = User.objects.all().order_by('-last_login')
    
    # Get the latest login activity for each user
    user_activities = {}
    for user in users:
        activities = UserLoginActivity.objects.filter(user=user).order_by('-login_datetime')
        if activities.exists():
            user_activities[user.id] = activities.first()
    
    context = {
        'users': users,
        'user_activities': user_activities,
    }
    return render(request, 'accounts/user_list.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email to admin
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Send to the same Gmail account
                fail_silently=False,
            )
            
            # Send auto-reply email to user
            send_mail(
                'Thank you for contacting SafeNet AI',
                f'Dear {name},\n\nThank you for reaching out to us. We have received your message about "{subject}" and our team will contact you soon.\n\nBest regards,\nThe SafeNet AI Team',
                settings.EMAIL_HOST_USER,
                [email],  # Send to user's email
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})
