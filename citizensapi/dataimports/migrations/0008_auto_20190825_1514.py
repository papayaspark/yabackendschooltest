# Generated by Django 2.2.4 on 2019-08-25 15:14

import dataimports.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataimports', '0007_auto_20190823_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='birth_date',
            field=models.DateField(validators=[dataimports.models.date_past]),
        ),
    ]
