# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-19 06:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20170719_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='introduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=32)),
                ('introduction', models.TextField(max_length=255)),
            ],
        ),
    ]