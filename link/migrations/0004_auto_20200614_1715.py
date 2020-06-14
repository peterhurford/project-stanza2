# Generated by Django 3.0.4 on 2020-06-14 22:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('link', '0003_link_benched'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0), verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='link',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0), verbose_name='date modified'),
        ),
    ]
