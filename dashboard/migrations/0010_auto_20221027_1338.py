# Generated by Django 3.2.5 on 2022-10-27 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20221018_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mydevice',
            name='contact',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='mydevicesnmpinterface',
            name='ifindex',
            field=models.BigIntegerField(default=0),
        ),
    ]
