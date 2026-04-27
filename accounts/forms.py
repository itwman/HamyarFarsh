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


class AdminUserCreateForm(UserCreationForm):
    """فرم افزودن کاربر جدید توسط مدیر با انتخاب نقش"""
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
    email = forms.EmailField(
        label='ایمیل (اختیاری)', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'})
    )
    role = forms.ChoiceField(
        label='نقش', choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        label='کاربر فعال باشد', required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_staff = forms.BooleanField(
        label='دسترسی به پنل ادمین جنگو (admin/)', required=False, initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
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
        fields = ('phone', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل باید 11 رقمی و با 09 شروع شود.')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('کاربری با این شماره موبایل وجود دارد.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone']
        user.role = self.cleaned_data['role']
        user.is_active = self.cleaned_data.get('is_active', True)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        # اگر نقش admin بود خودکار is_staff رو فعال کن
        if user.role == User.Role.ADMIN:
            user.is_staff = True
        if commit:
            user.save()
        return user


class AdminUserEditForm(forms.ModelForm):
    """فرم ویرایش کاربر توسط مدیر (بدون تغییر رمز)"""
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff', 'avatar')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control text-center', 'dir': 'ltr', 'maxlength': '11'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'phone': 'شماره موبایل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'role': 'نقش',
            'is_active': 'کاربر فعال',
            'is_staff': 'دسترسی به پنل ادمین جنگو',
            'avatar': 'تصویر پروفایل',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل باید 11 رقمی و با 09 شروع شود.')
        # بررسی تکرار (به جز خود کاربر)
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('کاربر دیگری با این شماره موبایل وجود دارد.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone']
        if user.role == User.Role.ADMIN:
            user.is_staff = True
        if commit:
            user.save()
        return user


class AdminPasswordResetForm(forms.Form):
    """فرم تغییر رمز کاربر توسط مدیر"""
    new_password1 = forms.CharField(
        label='رمز عبور جدید', min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'ltr'})
    )
    new_password2 = forms.CharField(
        label='تکرار رمز عبور', min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'dir': 'ltr'})
    )

    def clean(self):
        cd = super().clean()
        p1 = cd.get('new_password1')
        p2 = cd.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('دو رمز عبور یکسان نیستند.')
        return cd
