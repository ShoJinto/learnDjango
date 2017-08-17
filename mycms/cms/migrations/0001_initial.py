# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-12 07:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='webinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=32)),
                ('home', models.CharField(max_length=32)),
                ('contact', models.CharField(max_length=32)),
                ('about', models.CharField(max_length=32)),
            ],
        ),
    ]