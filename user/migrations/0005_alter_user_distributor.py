# Generated by Django 5.1.7 on 2025-03-30 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0002_distributor'),
        ('user', '0004_user_distributor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='distributor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_user', to='distributor.distributor'),
        ),
    ]
