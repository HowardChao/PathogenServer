# Generated by Django 2.1.5 on 2019-01-29 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_hash', '0002_auto_20190124_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletteruser',
            name='analysis_code',
            field=models.CharField(default='0', max_length=32),
        ),
    ]
