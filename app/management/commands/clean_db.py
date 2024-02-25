from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Unit.objects.all().delete()
        Calculation.objects.all().delete()
        CustomUser.objects.all().delete()