# Generated by Django 5.1.7 on 2025-04-07 11:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0003_alter_branch_distributor_alter_branch_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributorcustomer',
            name='distributor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='distributor.distributor'),
        ),
    ]
