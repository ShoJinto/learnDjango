# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-19 07:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_introduction'),
    ]

    operations = [
        migrations.CreateModel(
            name='feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_heading', models.CharField(max_length=32)),
                ('feature_muted', models.CharField(max_length=32)),
                ('feature_lead', models.TextField(max_length=255)),
            ],
        ),
    ]
