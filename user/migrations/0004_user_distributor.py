# Generated by Django 5.1.7 on 2025-03-30 21:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0002_distributor'),
        ('user', '0003_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='distributor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_profile', to='distributor.distributor'),
        ),
    ]
