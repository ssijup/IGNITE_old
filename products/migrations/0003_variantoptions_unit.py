# Generated by Django 4.1.5 on 2023-03-22 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_rename_minmun_amount_coupon_coupon_minmun_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='variantoptions',
            name='unit',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]