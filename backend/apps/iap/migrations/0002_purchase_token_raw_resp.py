from django.db import migrations, models
from django.utils import timezone


def backfill_purchase_token(apps, schema_editor):
    InAppPurchase = apps.get_model('iap', 'InAppPurchase')
    for p in InAppPurchase.objects.all():
        p.purchase_token = p.original_transaction_id
        p.created_at = p.purchase_date
        p.save(update_fields=['purchase_token', 'created_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('iap', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inapppurchase',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inapppurchase',
            name='is_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inapppurchase',
            name='purchase_token',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='inapppurchase',
            name='raw_store_resp',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_purchase_token, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='inapppurchase',
            name='purchase_token',
            field=models.TextField(unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inapppurchase',
            name='original_transaction_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='inapppurchase',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name='inapppurchase',
            index=models.Index(fields=['user', 'is_verified', 'expires_at'], name='iap_purchas_user_id_30c024_idx'),
        ),
    ]
