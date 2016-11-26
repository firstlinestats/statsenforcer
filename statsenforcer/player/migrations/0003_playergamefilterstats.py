# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-26 19:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playbyplay', '0004_auto_20161116_1805'),
        ('team', '0004_auto_20161125_1350'),
        ('player', '0002_auto_20161010_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerGameFilterStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[(b'all', b'All'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'OT')], db_index=True, max_length=4)),
                ('teamstrength', models.CharField(choices=[(b'all', b'All'), (b'even', b'Even Strength 5v5'), (b'pp', b'Power Play'), (b'pk', b'Short Handed'), (b'4v4', b'4v4'), (b'og', b'Opposing Goalie Pulled'), (b'tg', b'Team Goalie Pulled'), (b'3v3', b'3v3')], db_index=True, max_length=6)),
                ('scoresituation', models.CharField(choices=[(b'all', b'All'), (b't3+', b'Trailing by 3+'), (b't2', b'Trailing by 2'), (b't1', b'Trailing by 1'), (b't', b'Tied'), (b'l1', b'Leading by 1'), (b'l2', b'Leading by 2'), (b'l3+', b'Leading by 3+'), (b'w1', b'Within 1')], db_index=True, max_length=6)),
                ('toi', models.IntegerField(blank=True, null=True)),
                ('goals', models.IntegerField(blank=True, null=True)),
                ('assists1', models.IntegerField(blank=True, null=True)),
                ('assists2', models.IntegerField(blank=True, null=True)),
                ('points', models.IntegerField(blank=True, null=True)),
                ('corsiFor', models.IntegerField(blank=True, null=True)),
                ('corsiAgainst', models.IntegerField(blank=True, null=True)),
                ('fenwickFor', models.IntegerField(blank=True, null=True)),
                ('fenwickAgainst', models.IntegerField(blank=True, null=True)),
                ('goalsFor', models.IntegerField(blank=True, null=True)),
                ('goalsAgainst', models.IntegerField(blank=True, null=True)),
                ('fo_w', models.IntegerField(blank=True, null=True)),
                ('fo_l', models.IntegerField(blank=True, null=True)),
                ('hitFor', models.IntegerField(blank=True, null=True)),
                ('hitAgainst', models.IntegerField(blank=True, null=True)),
                ('penaltyFor', models.IntegerField(blank=True, null=True)),
                ('penaltyAgainst', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playbyplay.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.Team')),
            ],
        ),
    ]
