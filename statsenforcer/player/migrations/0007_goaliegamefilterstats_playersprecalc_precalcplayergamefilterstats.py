# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-06 00:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_auto_20170116_2202'),
        ('playbyplay', '0005_auto_20170116_2202'),
        ('player', '0006_auto_20170116_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalieGameFilterStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[(b'all', b'All'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'OT')], db_index=True, max_length=4)),
                ('teamstrength', models.CharField(choices=[(b'even', b'Even Strength 5v5'), (b'all', b'All'), (b'pp', b'Power Play'), (b'pk', b'Short Handed'), (b'4v4', b'4v4'), (b'og', b'Opposing Goalie Pulled'), (b'tg', b'Team Goalie Pulled'), (b'3v3', b'3v3')], db_index=True, max_length=6)),
                ('scoresituation', models.CharField(choices=[(b'all', b'All'), (b't3+', b'Trailing by 3+'), (b't2', b'Trailing by 2'), (b't1', b'Trailing by 1'), (b't', b'Tied'), (b'l1', b'Leading by 1'), (b'l2', b'Leading by 2'), (b'l3+', b'Leading by 3+'), (b'w1', b'Within 1')], db_index=True, max_length=6)),
                ('toi', models.IntegerField(blank=True, null=True)),
                ('savesUnknown', models.IntegerField(blank=True, null=True)),
                ('goalsUnknown', models.IntegerField(blank=True, null=True)),
                ('savesLow', models.IntegerField(blank=True, null=True)),
                ('goalsLow', models.IntegerField(blank=True, null=True)),
                ('savesMedium', models.IntegerField(blank=True, null=True)),
                ('goalsMedium', models.IntegerField(blank=True, null=True)),
                ('savesHigh', models.IntegerField(blank=True, null=True)),
                ('goalsHigh', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playbyplay.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.Team')),
            ],
        ),
    ]
