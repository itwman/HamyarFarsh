"""
کلاس سبد خرید (Session-based)
برای کاربران لاگین و غیر لاگین
"""
from decimal import Decimal
from django.conf import settings
from products.models import Product
from catalog.models import CarpetSize
from settings_app.models import SiteSettings


class Cart:
    """سبد خرید مبتنی بر Session"""
    
    def __init__(self, request):
        """مقداردهی اولیه سبد خرید"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # ایجاد سبد خالی
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
        self.site_settings = SiteSettings.get_solo()  # ✅ اصلاح شد
    
    def add(self, product, size, quantity=1, is_pair=False, override_quantity=False):
        """
        افزودن محصول به سبد یا بروزرسانی تعداد
        
        Args:
            product: محصول Product
            size: سایز CarpetSize
            quantity: تعداد
            is_pair: سفارش زوجی یا خیر
            override_quantity: جایگزینی تعداد یا اضافه کردن
        """
        product_id = str(product.id)
        size_id = str(size.id) if size else 'none'
        
        # کلید یکتا برای هر محصول+سایز
        cart_key = f"{product_id}_{size_id}"
        
        # محاسبه قیمت واحد
        unit_price = product.get_size_price(size)
        
        if cart_key not in self.cart:
            # افزودن آیتم جدید
            self.cart[cart_key] = {
                'product_id': product_id,
                'size_id': size_id,
                'quantity': 0,
                'price': str(unit_price),
                'is_pair': is_pair,
            }
        
        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        
        # بررسی زوج/فرد
        if is_pair and self.cart[cart_key]['quantity'] % 2 != 0:
            # اگر زوج است و تعداد فرد شد، یکی اضافه می‌کنیم
            self.cart[cart_key]['quantity'] += 1
        
        self.save()
    
    def save(self):
        """ذخیره سبد در session"""
        self.session.modified = True
    
    def remove(self, product_id, size_id):
        """حذف آیتم از سبد"""
        cart_key = f"{product_id}_{size_id}"
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()
    
    def update_quantity(self, product_id, size_id, quantity):
        """بروزرسانی تعداد"""
        cart_key = f"{product_id}_{size_id}"
        if cart_key in self.cart:
            if quantity > 0:
                self.cart[cart_key]['quantity'] = quantity
                
                # بررسی زوج/فرد
                if self.cart[cart_key].get('is_pair') and quantity % 2 != 0:
                    self.cart[cart_key]['quantity'] = quantity + 1
                
                self.save()
            else:
                self.remove(product_id, size_id)
    
    def clear(self):
        """خالی کردن سبد"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_total_price(self):
        """محاسبه مبلغ کل سبد"""
        total = 0
        for item in self.cart.values():
            total += int(item['price']) * item['quantity']
        return total
    
    def get_total_items(self):
        """تعداد کل آیتم‌ها"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def is_empty(self):
        """آیا سبد خالی است؟"""
        return len(self.cart) == 0
    
    def get_items(self):
        """
        دریافت لیست آیتم‌های سبد با اطلاعات کامل
        """
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids).select_related('album__manufacturer')
        
        size_ids = [item['size_id'] for item in self.cart.values() if item['size_id'] != 'none']
        sizes = {str(size.id): size for size in CarpetSize.objects.filter(id__in=size_ids)}
        
        items = []
        for cart_key, item_data in self.cart.items():
            try:
                product = next(p for p in products if str(p.id) == item_data['product_id'])
                size = sizes.get(item_data['size_id'])
                
                items.append({
                    'cart_key': cart_key,
                    'product': product,
                    'size': size,
                    'quantity': item_data['quantity'],
                    'unit_price': int(item_data['price']),
                    'total_price': int(item_data['price']) * item_data['quantity'],
                    'is_pair': item_data.get('is_pair', False),
                })
            except (StopIteration, Product.DoesNotExist):
                # محصول حذف شده - حذف از سبد
                del self.cart[cart_key]
                self.save()
        
        return items
    
    def check_free_shipping(self):
        """
        بررسی شرایط ارسال رایگان
        شرط: نقدی آنلاین + بالای حد مشخص شده
        """
        total = self.get_total_price()
        min_free_shipping = self.site_settings.free_shipping_min
        
        return total >= min_free_shipping
    
    def get_shipping_cost(self, payment_method='online_full'):
        """
        محاسبه هزینه ارسال
        """
        if payment_method == 'online_full' and self.check_free_shipping():
            return 0
        return self.site_settings.shipping_cost
    
    def __len__(self):
        """تعداد آیتم‌ها"""
        return len(self.cart)
    
    def __iter__(self):
        """ایتریت روی آیتم‌ها"""
        return iter(self.get_items())
