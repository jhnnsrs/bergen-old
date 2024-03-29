# Generated by Django 2.2.12 on 2020-04-06 08:05

from django.db import migrations
import larvik.fields
import larvik.storage.s3


class Migration(migrations.Migration):

    dependencies = [
        ('bioconverter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bioimage',
            name='file',
            field=larvik.fields.BioImageFileField(storage=larvik.storage.s3.MediaStorage(), upload_to='bioimages', verbose_name='bioimage'),
        ),
    ]
