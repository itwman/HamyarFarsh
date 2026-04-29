from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SiteSettings
from .forms import SiteSettingsForm


@login_required
def settings_view(request):
    """صفحه تنظیمات سایت - فقط مدیر"""
    if not request.user.is_admin_user:
        messages.error(request, 'شما دسترسی به این بخش ندارید.')
        return redirect('home')

    settings_obj = SiteSettings.get_solo()  # ✅ اصلاح شد

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'تنظیمات با موفقیت ذخیره شد.')
            return redirect('settings_app:site_settings')
        else:
            # نمایش خطاهای دقیق به کاربر
            error_count = sum(len(errors) for errors in form.errors.values())
            messages.error(
                request,
                f'خطا در ذخیره تنظیمات ({error_count} خطا). لطفاً فیلدهای قرمزرنگ را بررسی کنید.'
            )
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, 'settings_app/settings.html', {'form': form})
