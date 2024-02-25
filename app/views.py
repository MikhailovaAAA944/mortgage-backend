from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *
from .models import *


def get_draft_calculation():
    return Calculation.objects.filter(status=1).first()


@api_view(["GET"])
def search_unit(request):
    query = request.GET.get("query", "")

    products = Unit.objects.filter(status=1).filter(name__icontains=query)

    serializer = UnitSerializer(products, many=True)

    draft_calculation = get_draft_calculation()

    resp = {
        "units": serializer.data,
        "draft_calculation": draft_calculation.pk if draft_calculation else None
    }

    return Response(resp)


@api_view(['GET'])
def get_unit_by_id(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    serializer = UnitSerializer(unit, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def update_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_unit(request):
    Unit.objects.create()

    units = Unit.objects.all()
    serializer = UnitSerializer(units, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    unit.status = 2
    unit.save()

    units = Unit.objects.filter(status=1)
    serializer = UnitSerializer(units, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_unit_to_calculation(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    calculation = get_draft_calculation()

    if calculation is None:
        calculation = Calculation.objects.create()

    calculation.units.add(unit)
    calculation.save()

    serializer = CalculationSerializer(calculation.units, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    service = Unit.objects.get(pk=unit_id)

    return HttpResponse(service.image, content_type="image/png")


@api_view(["PUT"])
def update_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
def get_calculations(request):
    status = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    calculations = Calculation.objects.exclude(status__in=[1, 5])

    if status != -1:
        calculations = calculations.filter(status=status)

    if date_start and parse_datetime(date_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_start))

    if date_end and parse_datetime(date_end):
        calculations = calculations.filter(date_formation__lte=parse_datetime(date_end))

    serializer = CalculationSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_calculation_by_id(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    calculation.status = 1
    calculation.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 2
    calculation.date_formation = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = request_status
    calculation.date_complete = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.status = 5
    calculation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_unit_from_calculation(request, calculation_id, unit_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    calculation.units.remove(Unit.objects.get(pk=unit_id))
    calculation.save()

    serializer = UnitSerializer(calculation.units, many=True)

    return Response(serializer.data["units"])
