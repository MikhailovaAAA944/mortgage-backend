from rest_framework import serializers
from .models import *


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Unit
        # Поля, которые мы сериализуем (Все поля)
        fields = '__all__'


class CalculationSerializer(serializers.ModelSerializer):
    units = UnitSerializer(read_only=True, many=True)

    class Meta:
        # Модель, которую мы сериализуем
        model = Calculation
        # Поля, которые мы сериализуем (Все поля)
        fields = '__all__'