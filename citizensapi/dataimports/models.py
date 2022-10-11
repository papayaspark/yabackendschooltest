from django.db import models
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta


class DataImport(models.Model):
    # Модель набора данных (import)
    import_id = models.BigAutoField(primary_key=True)

    def __str__(self):
        return "DataImport #{}".format(self.import_id)


def date_past(value):
    # print("VALUE", value)
    # print("TODAY", datetime.today())
    # print("DIFFERENCE", value - datetime.today().date())
    # print("RESULT", (datetime.today().date() - value) < timedelta())
    if (datetime.today().date() - value) < timedelta(days=1):
        raise ValidationError(message="Date must be past")
    # return (datetime.today().date() - value) < timedelta(days=1)


class Citizen(models.Model):
    # Модель отдельного гражданина (citizen)
    data_import = models.ForeignKey(DataImport, related_name='citizens', on_delete=models.CASCADE)
    citizen_id = models.PositiveIntegerField()
    town = models.CharField(max_length=256)
    street = models.CharField(max_length=256)
    building = models.CharField(max_length=256)
    apartment = models.PositiveIntegerField()
    name = models.CharField(max_length=256)
    birth_date = models.DateField(validators=[date_past])
    gender = models.CharField(max_length=10, choices=[('male', 'male'), ('female', 'female')])
    relatives = models.ManyToManyField('self', blank=True)

    class Meta:
        unique_together = ('data_import', 'citizen_id')
