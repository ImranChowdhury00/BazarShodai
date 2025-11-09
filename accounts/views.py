from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


def signup(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'accounts/signup.html', {'form':form})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email= email, password= password)
        if user is not None:
            login(request, user)
            messages.success(request,"you have succcessfully logged in")
            return redirect("profile")
        else:
            messages.error("Invalid email or password")
    else:
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form':form})
    

@login_required
def user_logout(request):
    logout(request)
    return redirect('signup')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        user.email = request.POST.get("email", user.email)
        user.mobile = request.POST.get("mobile", user.mobile)
        user.address_1 = request.POST.get("address_line_1", user.address_1)
        user.address_2 = request.POST.get("address_line_2", user.address_2)
        user.city = request.POST.get("city", user.city)
        user.state = request.POST.get("state", user.state)
        user.country = request.POST.get("country", user.country)
        user.save()

        return redirect('profile')
    context = {
        'user_info': user
    }
    return render(request, 'accounts/profile.html', context)