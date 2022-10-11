from django.test import TestCase
from .models import DataImport, Citizen

class GetImportsTestCase(TestCase):
    def setUp(self):
        DataImport.objects.create(import_id=42)
        citizen_1 = {
            "citizen_id": 1,
            "town": "Москва", "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [2],
            "data_import": 42
        }
        citizen_2 = {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "01.04.1997",
            "gender": "male",
            "relatives": [1],
            "data_import": 42
        }

        Citizen.objects.create(**citizen_1)
        Citizen.objects.create(**citizen_2)


