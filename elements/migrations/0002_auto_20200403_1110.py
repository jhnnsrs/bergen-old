# Generated by Django 2.2.12 on 2020-04-03 11:10

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elements', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='representation',
            name='channels',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='transformation',
            name='channels',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
