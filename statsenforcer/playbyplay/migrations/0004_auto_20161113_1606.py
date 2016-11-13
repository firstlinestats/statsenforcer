# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-13 21:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0003_playmedia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playmedia',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='preview'),
        ),
        migrations.AlterField(
            model_name='playmedia',
            name='play',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='playbyplay.PlayByPlay'),
        ),
    ]
