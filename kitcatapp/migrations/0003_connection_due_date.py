# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kitcatapp', '0002_remove_connection_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
