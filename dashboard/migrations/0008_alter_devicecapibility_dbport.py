# Generated by Django 3.2.5 on 2022-10-13 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20221013_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicecapibility',
            name='dbport',
            field=models.CharField(blank=True, default=5432, max_length=50, null=True),
        ),
    ]
