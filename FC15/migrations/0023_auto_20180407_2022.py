# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-07 20:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FC15', '0022_auto_20180407_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileinfo',
            name='selected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='teaminfo',
            name='AI_selected',
            field=models.IntegerField(default=0),
        ),
    ]
