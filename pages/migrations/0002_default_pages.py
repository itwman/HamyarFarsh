"""ایجاد صفحات ایستای پیش‌فرض"""
from django.db import migrations


def create_default_pages(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')

    pages_data = [
        {
            'title': 'درباره ما',
            'slug': 'about-us',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 1,
            'content': '<h2>درباره همیار فرش</h2><p>همیار فرش یک پلتفرم آنلاین فروش فرش ماشینی است که با هدف ارائه بهترین محصولات با قیمت مناسب و خدمات عالی به مشتریان عزیز فعالیت می‌کند.</p>',
        },
        {
            'title': 'نحوه خرید',
            'slug': 'how-to-buy',
            'page_type': 'guide',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 2,
            'content': '<h2>راهنمای خرید از همیار فرش</h2><ol><li>محصول مورد نظر خود را انتخاب کنید</li><li>سایز و تعداد را مشخص کنید</li><li>به سبد خرید اضافه کنید</li><li>روش پرداخت را انتخاب کنید</li><li>سفارش خود را ثبت کنید</li></ol>',
        },
        {
            'title': 'شرایط ارسال',
            'slug': 'shipping-policy',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 3,
            'content': '<h2>شرایط ارسال</h2><p>ارسال به تمام نقاط ایران از طریق باربری انجام می‌شود.</p><ul><li><strong>ارسال رایگان:</strong> برای خریدهای نقدی آنلاین بالای 25 میلیون تومان</li><li><strong>هزینه ارسال:</strong> تا نزدیک‌ترین باربری به شهر شما</li><li><strong>زمان ارسال:</strong> 3 تا 7 روز کاری</li></ul>',
        },
        {
            'title': 'شرایط خرید اقساطی',
            'slug': 'installment-policy',
            'page_type': 'guide',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 4,
            'content': '<h2>شرایط خرید اقساطی</h2><h3>چک صیادی</h3><p>حداکثر 12 ماه، سقف 75 میلیون تومان</p><h3>طرح بتا (بانک رفاه)</h3><p>حداکثر 18 ماه، مخصوص بازنشستگان بانک رفاه</p>',
        },
        {
            'title': 'سوالات متداول',
            'slug': 'faq',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 5,
            'content': '<h2>سوالات متداول</h2><h3>آیا ارسال رایگان دارید؟</h3><p>بله، برای خریدهای نقدی آنلاین بالای 25 میلیون تومان ارسال رایگان است.</p><h3>آیا امکان خرید اقساطی وجود دارد؟</h3><p>بله، با چک صیادی تا 12 ماه و طرح بتا تا 18 ماه.</p><h3>آیا امکان مرجوعی وجود دارد؟</h3><p>در صورت انصراف، 50% بیعانه به‌عنوان جریمه کسر می‌شود.</p>',
        },
        {
            'title': 'تماس با ما',
            'slug': 'contact-us',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 6,
            'content': '<h2>تماس با ما</h2><p>از طریق راه‌های زیر می‌توانید با ما در ارتباط باشید:</p><ul><li>تلفن تماس</li><li>واتساپ</li><li>تلگرام</li><li>ایتا</li></ul>',
        },
        {
            'title': 'حریم خصوصی',
            'slug': 'privacy-policy',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 7,
            'content': '<h2>سیاست حریم خصوصی</h2><p>همیار فرش متعهد به حفظ حریم خصوصی کاربران است. اطلاعات شخصی شما فقط برای پردازش سفارشات استفاده می‌شود و به هیچ‌عنوان در اختیار اشخاص ثالث قرار نمی‌گیرد.</p>',
        },
        {
            'title': 'قوانین و مقررات',
            'slug': 'terms',
            'page_type': 'page',
            'status': 'published',
            'show_in_footer': True,
            'menu_order': 8,
            'content': '<h2>قوانین و مقررات</h2><p>با ثبت سفارش در سایت همیار فرش، شما قوانین زیر را می‌پذیرید:</p><ul><li>قیمت‌ها بر اساس قیمت روز محاسبه می‌شوند</li><li>بیعانه حداقل 10% مبلغ کل سفارش است</li><li>در صورت انصراف، 50% بیعانه به‌عنوان جریمه کسر می‌شود</li><li>سفارش سایز خاص فقط با تسویه کامل امکان‌پذیر است</li></ul>',
        },
    ]

    for data in pages_data:
        if not Page.objects.filter(slug=data['slug']).exists():
            Page.objects.create(**data)
            print(f"  -> صفحه '{data['title']}' ایجاد شد")


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_pages, migrations.RunPython.noop),
    ]
