# Generated by Django 4.1.7 on 2023-03-15 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_cartquantitys_delete_cartquantity'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CartQuantitys',
            new_name='CartQuantity',
        ),
    ]
