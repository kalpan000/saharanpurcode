# Generated by Django 3.2.5 on 2022-07-28 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_delete_storage_summary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topology',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='topo2', max_length=50)),
            ],
        ),
    ]
