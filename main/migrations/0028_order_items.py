# Generated by Django 4.2.13 on 2024-06-08 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_alter_order_apartment_number_remove_order_cart_items_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(related_name='orders', to='main.cartitem'),
        ),
    ]
