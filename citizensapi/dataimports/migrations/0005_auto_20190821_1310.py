# Generated by Django 2.2.4 on 2019-08-21 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataimports', '0004_auto_20190821_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizen',
            name='relatives',
            field=models.ManyToManyField(blank=True, limit_choices_to={'data_import__exact': models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='citizens', to='dataimports.DataImport')}, related_name='_citizen_relatives_+', to='dataimports.Citizen'),
        ),
    ]
