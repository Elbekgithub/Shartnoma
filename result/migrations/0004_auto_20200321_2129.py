# Generated by Django 3.0.4 on 2020-03-21 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0003_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='kurs',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='major',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
