# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-09-12 10:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_constant_contact', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmarketingcampaign',
            name='new_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=None),
            preserve_default=False,
        ),
    ]