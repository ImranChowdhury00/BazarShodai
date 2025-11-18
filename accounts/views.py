from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator


def signup(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            messages.info(request, "We have sent you an verfication email")
            return redirect("login")
        else:
            return redirect("signup")
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'accounts/signup.html', {'form':form})


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, "Your email has been verified successfully.")
        return redirect("login")
    else:
        messages.error(request, "The verification link is invalid or has expired.")
        return redirect("signup")


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email= email, password= password)
        if not user:
            messages.error(request, "Invalid username or password.")
            return redirect("profile")
        elif not user.is_verified:
            messages.error(request, "Your email is not verified yet.")
            return redirect("profile")
        else:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect("profile")
    else:
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form':form})
    

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        user.email = request.POST.get("email", user.email)
        user.mobile = request.POST.get("mobile", user.mobile)
        user.address_1 = request.POST.get("address_line_1", user.address_line_1)
        user.address_2 = request.POST.get("address_line_2", user.address_line_2)
        user.city = request.POST.get("city", user.city)
        user.state = request.POST.get("state", user.state)
        user.country = request.POST.get("country", user.country)
        user.save()

        return redirect('profile')
    context = {
        'user_info': user
    }
    return render(request, 'accounts/profile.html', context)

