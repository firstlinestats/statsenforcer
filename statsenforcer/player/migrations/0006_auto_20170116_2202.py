# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-17 03:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0005_playergamefilterstats_neutralzonestarts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playergamefilterstats',
            name='teamstrength',
            field=models.CharField(choices=[(b'even', b'Even Strength 5v5'), (b'all', b'All'), (b'pp', b'Power Play'), (b'pk', b'Short Handed'), (b'4v4', b'4v4'), (b'og', b'Opposing Goalie Pulled'), (b'tg', b'Team Goalie Pulled'), (b'3v3', b'3v3')], db_index=True, max_length=6),
        ),
    ]