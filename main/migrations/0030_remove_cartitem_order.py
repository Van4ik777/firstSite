# Generated by Django 4.2.13 on 2024-06-08 13:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_remove_order_items_cartitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='order',
        ),
    ]
