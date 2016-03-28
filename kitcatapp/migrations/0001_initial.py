# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('due_date', models.DateTimeField(default=0)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('date_met', models.DateField(null=True, blank=True)),
                ('how_met', models.CharField(max_length=400, blank=True)),
                ('about', models.TextField(blank=True)),
                ('frequency', models.CharField(max_length=200, choices=[(b'1', b'Daily'), (b'7', b'Weekly'), (b'14', b'Bi-Weekly'), (b'28', b'Monthly'), (b'90', b'Every Three Months'), (b'180', b'Every Six Months'), (b'365', b'Yearly')])),
            ],
        ),
        migrations.AddField(
            model_name='connection',
            name='contact',
            field=models.ForeignKey(to='kitcatapp.Contact'),
        ),
    ]
