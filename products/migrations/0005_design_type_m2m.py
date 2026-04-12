# Migration: Convert design_type from ForeignKey to ManyToManyField
# Based on actual DB state: design_type_id is gone, design_type_old_id exists, no M2M table yet
from django.db import migrations, models


def create_m2m_and_migrate(apps, schema_editor):
    """ساخت جدول M2M و انتقال داده‌ها از design_type_old_id"""
    cursor = schema_editor.connection.cursor()

    # 1. ساخت جدول M2M
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `products_product_design_type` (
            `id` bigint AUTO_INCREMENT PRIMARY KEY,
            `product_id` bigint NOT NULL,
            `designtype_id` bigint NOT NULL,
            UNIQUE KEY `products_product_design_type_uniq` (`product_id`, `designtype_id`),
            CONSTRAINT `pp_dt_product_fk` FOREIGN KEY (`product_id`) 
                REFERENCES `products_product` (`id`) ON DELETE CASCADE,
            CONSTRAINT `pp_dt_designtype_fk` FOREIGN KEY (`designtype_id`) 
                REFERENCES `catalog_designtype` (`id`) ON DELETE CASCADE
        )
    """)
    print("  -> جدول M2M ساخته شد")

    # 2. انتقال داده‌ها از design_type_old_id
    cursor.execute("""
        SELECT id, design_type_old_id FROM products_product 
        WHERE design_type_old_id IS NOT NULL
    """)
    rows = cursor.fetchall()
    for product_id, dt_id in rows:
        cursor.execute(
            "INSERT IGNORE INTO products_product_design_type (product_id, designtype_id) VALUES (%s, %s)",
            [product_id, dt_id]
        )
    print(f"  -> {len(rows)} رکورد منتقل شد")

    # 3. حذف FK constraint از design_type_old_id
    cursor.execute("""
        SELECT CONSTRAINT_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'products_product'
          AND COLUMN_NAME = 'design_type_old_id'
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    for row in cursor.fetchall():
        fk_name = row[0]
        print(f"  -> حذف FK: {fk_name}")
        cursor.execute(f"ALTER TABLE products_product DROP FOREIGN KEY `{fk_name}`")

    # 4. حذف index های design_type_old_id
    cursor.execute("""
        SELECT DISTINCT INDEX_NAME 
        FROM information_schema.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'products_product'
          AND COLUMN_NAME = 'design_type_old_id'
    """)
    for row in cursor.fetchall():
        idx_name = row[0]
        print(f"  -> حذف index: {idx_name}")
        try:
            cursor.execute(f"DROP INDEX `{idx_name}` ON products_product")
        except Exception:
            pass

    # 5. حذف ستون قدیمی
    cursor.execute("ALTER TABLE products_product DROP COLUMN design_type_old_id")
    print("  -> ستون design_type_old_id حذف شد")


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_rebuild_productvideo'),
        ('catalog', '0003_seed_default_data'),
    ]

    operations = [
        # اجرای SQL خام
        migrations.RunPython(create_m2m_and_migrate, migrations.RunPython.noop),

        # همگام‌سازی state جنگو با واقعیت دیتابیس
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # به جنگو بگو index قدیمی حذف شده
                migrations.RemoveIndex(
                    model_name='product',
                    name='products_pr_design__02f2ef_idx',
                ),
                # به جنگو بگو FK قدیمی حذف شده و M2M جایگزین شده
                migrations.RemoveField(
                    model_name='product',
                    name='design_type',
                ),
                migrations.AddField(
                    model_name='product',
                    name='design_type',
                    field=models.ManyToManyField(
                        blank=True,
                        related_name='products',
                        to='catalog.designtype',
                        verbose_name='نوع طرح',
                    ),
                ),
            ],
            database_operations=[],  # همه کار بالا انجام شده
        ),
    ]
