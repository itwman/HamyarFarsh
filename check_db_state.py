"""بررسی وضعیت واقعی دیتابیس"""
import os, sys, django
sys.path.insert(0, r'C:\xampp\htdocs\Hamyarfarsh')
os.environ['DJANGO_SETTINGS_MODULE'] = 'hamyarfarsh.settings'
django.setup()

from django.db import connection

cursor = connection.cursor()

# بررسی ستون‌های جدول products_product
cursor.execute("""
    SELECT COLUMN_NAME FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'products_product'
    ORDER BY ORDINAL_POSITION
""")
cols = [r[0] for r in cursor.fetchall()]
print("=== ستون‌های products_product ===")
for c in cols:
    print(f"  {c}")

print(f"\ndesign_type_id وجود داره؟ {'بله' if 'design_type_id' in cols else 'خیر'}")

# بررسی جدول M2M
cursor.execute("""
    SELECT TABLE_NAME FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME LIKE '%design_type%'
""")
tables = [r[0] for r in cursor.fetchall()]
print(f"\nجدول‌های design_type: {tables}")

# بررسی FK constraints
cursor.execute("""
    SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'products_product'
      AND COLUMN_NAME = 'design_type_id'
""")
fks = cursor.fetchall()
print(f"\nFK constraints روی design_type_id: {fks}")

# بررسی index ها
cursor.execute("""
    SELECT INDEX_NAME, COLUMN_NAME 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'products_product'
      AND COLUMN_NAME = 'design_type_id'
""")
idxs = cursor.fetchall()
print(f"Index ها روی design_type_id: {idxs}")

# بررسی migration state
cursor.execute("""
    SELECT name, applied FROM django_migrations 
    WHERE app = 'products' ORDER BY id
""")
migs = cursor.fetchall()
print(f"\n=== Migration state ===")
for m in migs:
    print(f"  {m[0]} - applied: {m[1]}")
