from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class PhoneAuthForm(AuthenticationForm):
    """فرم ورود با شماره موبایل"""
    username = forms.CharField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '09121234567',
            'dir': 'ltr',
            'maxlength': '11',
            'autocomplete': 'tel',
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور',
            'dir': 'ltr',
        })
    )


class CustomerRegisterForm(UserCreationForm):
    """فرم ثبت‌نام مشتری"""
    phone = forms.CharField(
        label='شماره موبایل', max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '09121234567',
            'dir': 'ltr',
        })
    )
    first_name = forms.CharField(
        label='نام', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='نام خانوادگی', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'ltr'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'ltr'})
    )

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone']
        user.role = User.Role.CUSTOMER
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
