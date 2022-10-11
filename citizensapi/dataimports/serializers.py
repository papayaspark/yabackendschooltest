import json
from collections import defaultdict

from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError as JsonValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import DataImport, Citizen


class CitizenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Citizen
        fields = ('citizen_id',
                  'town',
                  'street',
                  'building',
                  'apartment',
                  'name',
                  'birth_date',
                  'gender',
                  'relatives'
                  )
        read_only_fields = ('relatives',)

    def to_representation(self, instance):
        instance_dict = super().to_representation(instance)
        instance_dict['relatives'] = [citizen.citizen_id
                                      for citizen in Citizen.objects.filter(pk__in=instance_dict['relatives'])]
        instance_dict['birth_date'] = '.'.join(instance_dict['birth_date'].split('-')[::-1])
        return instance_dict


class DataImportSerializer(serializers.ModelSerializer):
    citizens = CitizenSerializer(many=True, required=True)

    class Meta:
        model = DataImport
        fields = ['import_id', 'citizens']

    def create(self, validated_data):
        data_import = DataImport.objects.create()
        citizens_data = validated_data.pop('citizens')
        # Создаем все объекты
        id_cid_dict = {}
        for citizen_dict in citizens_data:
            instance = Citizen.objects.create(data_import=data_import, **citizen_dict)
            id_cid_dict[citizen_dict['citizen_id']] = instance.id
            instance.relatives.set([])
        # Создаем связи между ними
        for cid in validated_data['relations_dict']:
            rel_list = [id_cid_dict[i] for i in validated_data['relations_dict'][cid]]
            relatives = Citizen.objects.filter(data_import__exact=data_import, pk__in=rel_list)
            instance = Citizen.objects.get(data_import__exact=data_import, pk=id_cid_dict[cid])
            instance.relatives.set(relatives)
        return data_import

    def validate(self, data):
        with open('dataimports/schemas/post_schema.json', 'r') as schema_file:
            schema = json.load(schema_file)
        try:
            json_validate(self.initial_data, schema)
        except JsonValidationError as exc:
            raise ValidationError("Invalid JSON")

        # Собираем все связи (направление важно!) во множество для проверки консистентности
        # Используем initial_data, т.к. в нем они еще не преобразованы в объекты Citizen
        citizens = self.initial_data['citizens']
        relations_set = set()
        relations_dict = defaultdict(list)
        for c in citizens:
            current_relatives = c['relatives']
            for r in current_relatives:
                relations_set.add((c['citizen_id'], r))
                relations_dict[c['citizen_id']].append(r)

        # Проверяем родственные связи
        for r1, r2 in relations_set:
            if not ((r2, r1) in relations_set):
                raise ValidationError("Inconsistent relations")

        # Убираем все связи из data, т.к. m2m-поля нельзя инициализировать просто так
        data['relations_dict'] = relations_dict
        return data
