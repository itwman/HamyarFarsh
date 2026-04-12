# Migration: Upgrade ProductVideo from basic to full model with processing fields
# Generated manually for HamyarFarsh

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_delete_old_videos'),
    ]

    operations = [
        # ===== حذف جدول قدیمی ProductVideo و ساخت مجدد =====
        # چون داده‌ها در 0003 پاک شدن، ساده‌تره جدول رو drop و rebuild کنیم
        migrations.DeleteModel(
            name='ProductVideo',
        ),
        migrations.CreateModel(
            name='ProductVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # فایل‌های ویدیو
                ('original_file', models.FileField(upload_to='products/videos/originals/', verbose_name='ویدیو اصلی')),
                ('video_720p', models.FileField(blank=True, null=True, upload_to='products/videos/720p/', verbose_name='ویدیو 720p')),
                ('video_480p', models.FileField(blank=True, null=True, upload_to='products/videos/480p/', verbose_name='ویدیو 480p')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='products/videos/thumbnails/', verbose_name='تصویر پیش‌نمایش')),
                # اطلاعات فنی
                ('duration', models.FloatField(blank=True, null=True, verbose_name='مدت زمان (ثانیه)')),
                ('original_width', models.IntegerField(blank=True, null=True, verbose_name='عرض اصلی (پیکسل)')),
                ('original_height', models.IntegerField(blank=True, null=True, verbose_name='ارتفاع اصلی (پیکسل)')),
                ('original_size', models.BigIntegerField(blank=True, null=True, verbose_name='حجم اصلی (بایت)')),
                ('size_720p', models.BigIntegerField(blank=True, null=True, verbose_name='حجم 720p (بایت)')),
                ('size_480p', models.BigIntegerField(blank=True, null=True, verbose_name='حجم 480p (بایت)')),
                # وضعیت پردازش
                ('processing_status', models.CharField(
                    choices=[('pending', 'در صف پردازش'), ('processing', 'در حال پردازش'), ('completed', 'تکمیل شده'), ('failed', 'خطا در پردازش')],
                    default='pending', max_length=20, verbose_name='وضعیت پردازش'
                )),
                ('processing_error', models.TextField(blank=True, verbose_name='خطای پردازش')),
                ('processing_progress', models.IntegerField(default=0, verbose_name='درصد پیشرفت پردازش')),
                ('processed_at', models.DateTimeField(blank=True, null=True, verbose_name='زمان پردازش')),
                # متاداده
                ('title', models.CharField(blank=True, max_length=200, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('alt_text', models.CharField(blank=True, max_length=200, verbose_name='متن جایگزین (alt)')),
                # SEO
                ('seo_title', models.CharField(blank=True, max_length=200, verbose_name='عنوان SEO ویدیو')),
                ('seo_description', models.TextField(blank=True, verbose_name='توضیحات SEO ویدیو')),
                # نمایش
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_featured', models.BooleanField(default=False, verbose_name='ویدیو شاخص')),
                ('show_in_gallery', models.BooleanField(default=True, verbose_name='نمایش در گالری ویدیو')),
                # آمار
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')),
                # تاریخ
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
                # روابط
                ('product', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    related_name='videos',
                    to='products.product',
                    verbose_name='محصول'
                )),
            ],
            options={
                'verbose_name': 'ویدیوی محصول',
                'verbose_name_plural': 'ویدیوهای محصولات',
                'ordering': ['order', '-uploaded_at'],
            },
        ),
        # Index ها
        migrations.AddIndex(
            model_name='productvideo',
            index=models.Index(fields=['processing_status'], name='pv_processing_status_idx'),
        ),
        migrations.AddIndex(
            model_name='productvideo',
            index=models.Index(fields=['show_in_gallery'], name='pv_show_in_gallery_idx'),
        ),
        migrations.AddIndex(
            model_name='productvideo',
            index=models.Index(fields=['is_featured'], name='pv_is_featured_idx'),
        ),
    ]
