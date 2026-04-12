from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from datetime import date

from payments.models import InstallmentPlan, Installment


class Command(BaseCommand):
    help = 'ایجاد اقساط برای طرح‌های اقساطی تأیید شده'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plan-id',
            type=int,
            help='شناسه طرح اقساط (اختیاری - اگر نباشد همه طرح‌های تأیید شده پردازش می‌شوند)'
        )

    def handle(self, *args, **options):
        plan_id = options.get('plan_id')
        
        if plan_id:
            plans = InstallmentPlan.objects.filter(id=plan_id, is_confirmed=True)
        else:
            # فقط طرح‌هایی که قسط ندارند
            plans = InstallmentPlan.objects.filter(
                is_confirmed=True,
                installments__isnull=True
            ).distinct()
        
        if not plans.exists():
            self.stdout.write(self.style.WARNING('هیچ طرح اقساطی برای پردازش یافت نشد.'))
            return
        
        created_count = 0
        
        for plan in plans:
            # بررسی اینکه قبلاً قسط ساخته نشده باشد
            if plan.installments.exists():
                self.stdout.write(
                    self.style.WARNING(f'طرح #{plan.id} قبلاً دارای اقساط است.')
                )
                continue
            
            # تاریخ شروع
            start_date = plan.first_due_date or date.today()
            
            # محاسبه فاصله بین اقساط
            if plan.period == 'monthly':
                delta_months = 1
            else:  # bimonthly
                delta_months = 2
            
            # ایجاد اقساط
            for i in range(1, plan.num_installments + 1):
                due_date = start_date + relativedelta(months=(i - 1) * delta_months)
                
                Installment.objects.create(
                    plan=plan,
                    installment_number=i,
                    amount=plan.installment_amount,
                    due_date=due_date,
                    status='pending'
                )
                created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ طرح #{plan.id}: {plan.num_installments} قسط ایجاد شد'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ در مجموع {created_count} قسط ایجاد شد.')
        )
