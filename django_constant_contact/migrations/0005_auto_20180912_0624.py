# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-09-12 10:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_constant_contact', '0004_remove_emailmarketingcampaign_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailmarketingcampaign',
            old_name='new_data',
            new_name='data',
        ),
    ]