# Generated by Django 3.0.4 on 2020-03-21 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0004_auto_20200321_2129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='kurs',
        ),
    ]
