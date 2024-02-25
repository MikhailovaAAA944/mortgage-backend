import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user


def get_draft_calculation(request):
    user = identity_user(request)

    if user is None:
        return None

    calculation = Calculation.objects.filter(owner_id=user.id).filter(status=1).first()

    return calculation


@api_view(["GET"])
def search_units(request):
    query = request.GET.get("query", "")

    unit = Unit.objects.filter(status=1).filter(name__icontains=query)

    serializer = UnitSerializer(unit, many=True)

    draft_calculation = get_draft_calculation(request)

    resp = {
        "units": serializer.data,
        "draft_calculation_id": draft_calculation.pk if draft_calculation else None
    }

    return Response(resp)


@api_view(["GET"])
def get_unit_by_id(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_unit(request):
    unit = Unit.objects.create()

    serializer = UnitSerializer(unit)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_unit(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    unit.status = 2
    unit.save()

    unit = Unit.objects.filter(status=1)
    serializer = UnitSerializer(unit, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_unit_to_calculation(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    calculation = get_draft_calculation(request)

    if calculation is None:
        calculation = Calculation.objects.create()
        calculation.date_perform = timezone.now()
        calculation.save()

    if calculation.units.contains(unit):
        return Response(status=status.HTTP_409_CONFLICT)

    calculation.units.add(unit)
    calculation.owner = identity_user(request)
    calculation.save()

    serializer = CalculationSerializer(calculation)
    return Response(serializer.data)


@api_view(["GET"])
def get_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)

    return HttpResponse(unit.image, content_type="image/png")


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_unit_image(request, unit_id):
    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    unit = Unit.objects.get(pk=unit_id)
    serializer = UnitSerializer(unit, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_calculations(request):
    user = identity_user(request)

    status_id = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    calculations = Calculation.objects.exclude(status__in=[1, 5])

    if not user.is_moderator:
        calculations = calculations.filter(owner=user)

    if status_id > 0:
        calculations = calculations.filter(status=status_id)

    if date_start and parse_datetime(date_start):
        calculations = calculations.filter(date_formation__gte=parse_datetime(date_start))

    if date_end and parse_datetime(date_end):
        calculations = calculations.filter(date_formation__lte=parse_datetime(date_end))

    serializer = CalculationsSerializer(calculations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_calculation_by_id(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    calculation.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsRemoteService])
def update_calculation_state(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    serializer = CalculationSerializer(calculation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    calculation.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)

    calculation.status = 2
    calculation.date_formation = timezone.now()
    calculation.save()

    # calculate_state(calculation_id)

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


def calculate_state(calculation_id):
    data = {
        "calculation_id": calculation_id
    }

    requests.post("http://127.0.0.1:8080/calc_state/", json=data, timeout=3)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation = Calculation.objects.get(pk=calculation_id)

    if calculation.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    calculation.moderator = identity_user(request)
    calculation.status = request_status
    calculation.date_complete = timezone.now()
    calculation.save()

    serializer = CalculationSerializer(calculation)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def delete_unit_from_calculation(request, calculation_id, unit_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Unit.objects.filter(pk=unit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    calculation = Calculation.objects.get(pk=calculation_id)
    calculation.units.remove(Unit.objects.get(pk=unit_id))
    calculation.save()

    if calculation.units.count() == 0:
        calculation.delete()
        return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }

    return Response(user_data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    message = {
        'message': 'User registered successfully',
        'user_id': user.id,
        "access_token": access_token
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    token = get_access_token(request)

    if token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if token in cache:
        message = {"message": "Token in blacklist"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    user = CustomUser.objects.get(pk=user_id)
    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    message = {
        "message": "Вы успешно вышли из аккаунта"
    }

    return  Response(message, status=status.HTTP_200_OK)
