# Generated by Django 2.1.5 on 2019-02-03 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataanalysis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(upload_to='photos/'),
        ),
    ]
