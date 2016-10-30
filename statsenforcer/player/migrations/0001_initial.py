# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 20:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('team', '0001_initial'),
        ('playbyplay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompiledGoalieGameStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField()),
                ('strength', models.CharField(max_length=4)),
                ('shotsLow', models.IntegerField()),
                ('savesLow', models.IntegerField()),
                ('shotsMedium', models.IntegerField()),
                ('savesMedium', models.IntegerField()),
                ('shotsHigh', models.IntegerField()),
                ('savesHigh', models.IntegerField()),
                ('toi', models.TimeField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playbyplay.Game')),
            ],
        ),
        migrations.CreateModel(
            name='CompiledPlayerGameStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField()),
                ('strength', models.CharField(max_length=4)),
                ('goals', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('assists2', models.IntegerField()),
                ('gf', models.IntegerField()),
                ('ga', models.IntegerField()),
                ('pnDrawn', models.IntegerField()),
                ('pn', models.IntegerField()),
                ('pdo', models.DecimalField(decimal_places=2, max_digits=6)),
                ('sf', models.IntegerField()),
                ('msf', models.IntegerField()),
                ('bsf', models.IntegerField()),
                ('onsf', models.IntegerField()),
                ('onmsf', models.IntegerField()),
                ('onbsf', models.IntegerField()),
                ('offsf', models.IntegerField()),
                ('offmsf', models.IntegerField()),
                ('offbsf', models.IntegerField()),
                ('sa', models.IntegerField()),
                ('msa', models.IntegerField()),
                ('bsa', models.IntegerField()),
                ('zso', models.IntegerField()),
                ('zsn', models.IntegerField()),
                ('zsd', models.IntegerField()),
                ('toi', models.TimeField()),
                ('ihsc', models.IntegerField()),
                ('isc', models.IntegerField()),
                ('sc', models.IntegerField()),
                ('hscf', models.IntegerField()),
                ('hsca', models.IntegerField()),
                ('sca', models.IntegerField()),
                ('fo_w', models.IntegerField()),
                ('fo_l', models.IntegerField()),
                ('hit', models.IntegerField()),
                ('hitt', models.IntegerField()),
                ('gv', models.IntegerField()),
                ('tk', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playbyplay.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('fullName', models.CharField(max_length=100)),
                ('link', models.URLField()),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('primaryNumber', models.IntegerField(blank=True, null=True)),
                ('primaryPositionCode', models.CharField(choices=[(b'R', b'Right Wing'), (b'C', b'Center'), (b'L', b'Left Wing'), (b'D', b'Defenseman'), (b'G', b'Goalie')], max_length=1)),
                ('birthDate', models.DateField()),
                ('birthCity', models.CharField(max_length=100)),
                ('birthStateProvince', models.CharField(max_length=100)),
                ('birthCountry', models.CharField(max_length=100)),
                ('height', models.CharField(max_length=10)),
                ('weight', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('rookie', models.BooleanField(default=False)),
                ('shootsCatches', models.CharField(blank=True, max_length=1, null=True)),
                ('rosterStatus', models.CharField(choices=[(b'Y', b'Yes'), (b'N', b'No'), (b'I', b'IR')], max_length=1)),
                ('currentTeam', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team.Team')),
            ],
        ),
        migrations.AddField(
            model_name='compiledplayergamestats',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Player'),
        ),
        migrations.AddField(
            model_name='compiledgoaliegamestats',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Player'),
        ),
    ]