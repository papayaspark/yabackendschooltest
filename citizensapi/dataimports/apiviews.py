from datetime import date
from json import load

from numpy import percentile, around
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError as JsonValidationError

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import status

from .models import DataImport, Citizen
from .serializers import DataImportSerializer, CitizenSerializer


class DataImportCitizens(CreateAPIView):
    queryset = DataImport.objects.all()
    serializer_class = DataImportSerializer

    def post(self, request, *args, **kwargs):
        instance = self.create(request, *args, **kwargs)
        return JsonResponse({ "data": { "import_id": instance.data['import_id']} }, status=status.HTTP_201_CREATED)

    def get(self, request, pk, *args, **kwargs):
        try:
            instance = DataImport.objects.get(import_id=pk)
        except DataImport.DoesNotExist:
            return JsonResponse({'detail': 'Import not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        data = serializer.data
        data.pop('import_id')
        return JsonResponse({'data': data})


class PatchCitizens(UpdateAPIView):
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer

    def validate_request(self, request):
        # Проверяем полученные данные на соответствие требованиям
        with open('dataimports/schemas/patch_schema.json', 'r') as schema_file:
            schema = load(schema_file)
        try:
            json_validate(request.data, schema)
        except JsonValidationError:
            raise ValidationError({"detail": "Invalid JSON"})

    def patch(self, request, import_pk, citizen_pk, *args, **kwargs):
        self.import_pk = import_pk
        self.citizen_pk = citizen_pk
        self.validate_request(request)
        instance = get_object_or_404(Citizen, data_import_id=import_pk, citizen_id=citizen_pk)
        # Обновляем связи
        if 'relatives' in request.data:
            old_relatives_obj = instance.relatives.all()
            new_relatives = request.data.pop('relatives')
            # Проверяем, есть граждане с такими id
            for r in new_relatives:
                try:
                    Citizen.objects.get(data_import_id=import_pk, citizen_id=r)
                except Citizen.DoesNotExist:
                    return JsonResponse({'detail': 'User with id {} does not exist'.format(r)}, status=status.HTTP_400_BAD_REQUEST)
            new_relatives_obj = Citizen.objects.filter(data_import_id=import_pk, citizen_id__in=new_relatives)
            # Убрать ссылки у всех старых объектов на этот
            for c in old_relatives_obj:
                c.relatives.remove(instance)
            # Добавить всем новым ссылки на этот
            for c in new_relatives_obj:
                c.relatives.add(instance)
            # Обновить сам объект
            instance.relatives.set(new_relatives_obj)

        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        # Этот метод переопределен, чтобы иметь возможность поиска по id импорта и гражданина
        return get_object_or_404(Citizen, data_import_id=self.import_pk, citizen_id=self.citizen_pk)


class GetCitizensBirthdays(APIView):

    def get(self, request, pk, *args, **kwargs):
        result = {}
        for month in range(1, 13):
            result[str(month)] = []
            for citizen in Citizen.objects.filter(data_import_id=pk):
                present_count = 0
                for r in citizen.relatives.all():
                    if r.birth_date.month == month:
                        present_count += 1
                if present_count:
                    result[str(month)].append({"citizen_id": citizen.citizen_id, "presents": present_count})
        return JsonResponse({"data": result})


class GetStats(APIView):

    def get(self, request, pk, *args, **kwargs):
        result = []
        towns = [c.town for c in Citizen.objects.filter(data_import_id=pk)]
        towns = list(set(towns))
        today = date.today()
        for t in towns:
            townsfolk = Citizen.objects.filter(data_import_id=pk, town=t)
            townsfolk_ages = []
            for c in townsfolk:
                townsfolk_ages.append(int((today - c.birth_date).days / 365.25))
            percentiles = [percentile(townsfolk_ages, p, interpolation='linear') for p in [50, 75, 99]]
            rounded = around(percentiles, decimals=2)
            result.append({"town": t, "p50": rounded[0], "p75": rounded[1], "p99": rounded[2]})
        return JsonResponse({"data": result})
