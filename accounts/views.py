from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PhoneAuthForm, CustomerRegisterForm, ProfileForm


def home_view(request):
    """صفحه اصلی — رندر پویا از home_manager"""
    from home_manager.views import home_view as hm_home
    return hm_home(request)


def login_view(request):
    """ورود کاربر"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = PhoneAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'خوش آمدید {user.get_full_name() or user.phone}')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = PhoneAuthForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """ثبت‌نام مشتری جدید"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد!')
            return redirect('home')
    else:
        form = CustomerRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """خروج کاربر"""
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید.')
    return redirect('home')


@login_required
def profile_view(request):
    """پروفایل کاربر"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل شما به‌روزرسانی شد.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
