# Generated by Django 2.2.12 on 2020-04-03 11:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('answers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Visualizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('settings', models.CharField(max_length=1000)),
                ('name', models.CharField(max_length=100)),
                ('channel', models.CharField(blank=True, max_length=100, null=True)),
                ('defaultsettings', models.CharField(max_length=400)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Visualizing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statuscode', models.IntegerField(blank=True, null=True)),
                ('statusmessage', models.CharField(blank=True, max_length=500, null=True)),
                ('settings', models.CharField(max_length=1000)),
                ('nodeid', models.CharField(blank=True, max_length=400, null=True)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='answers.Answer')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('visualizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizers.Visualizer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(blank=True, max_length=300, null=True)),
                ('nodeid', models.CharField(blank=True, max_length=400, null=True)),
                ('vid', models.CharField(max_length=4000)),
                ('name', models.CharField(blank=True, max_length=4000, null=True)),
                ('htmlfile', models.FileField(blank=True, null=True, upload_to='profiles')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='answers.Answer')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExcelExport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature', models.CharField(blank=True, max_length=300, null=True)),
                ('nodeid', models.CharField(blank=True, max_length=400, null=True)),
                ('vid', models.CharField(max_length=4000)),
                ('name', models.CharField(blank=True, max_length=4000, null=True)),
                ('excelfile', models.FileField(blank=True, null=True, upload_to='excels')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='answers.Answer')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
