import random

from django.core import management
from django.core.management.base import BaseCommand
from ...models import *
from .utils import random_date, random_timedelta


def add_units():
    Unit.objects.create(
        name="Страховка",
        description="Страхова́ние — отношения между страхователем и страховщиком по защите имущественных интересов физических и юридических лиц при наступлении определённых событий за счёт денежных фондов, формируемых из уплачиваемых ими страховых взносов.",
        image="units/1.jpg"
    )

    Unit.objects.create(
        name="Ежемесячные платежи",
        description="Ежемесячный платеж состоит из платежа по основному долгу и начисленным процентам. Соотношение основного долга и процентов в платеже может быть разным. Поговорим об этом ниже. Если заемщик допускает просрочку, к платежу могут добавиться штрафы и начисления за пропуск оплаты.",
        image="units/2.jpg"
    )

    Unit.objects.create(
        name="Аннуитет",
        description="Аннуитет — это схема выплат по финансовому инструменту (облигации, кредиту и пр.), при которой долг гасят равными суммами и через равные промежутки времени. В саму выплату входит не только задолженность, но и набежавший процент.",
        image="units/3.jpg"
    )

    Unit.objects.create(
        name="Равные доли",
        description="Платежи равными долями – определенный договором способ возврата кредита равными по величине платежами, которые рассчитываются путем деления основного долга и процентов, начисленных за весь срок пользования кредитом, на количество платежных периодов.",
        image="units/4.jpg"
    )

    Unit.objects.create(
        name="Дифференцированный платеж",
        description="Основной долг делят на количество выплат за весь срок ипотеки — получаются равные доли. Каждый месяц к ним прибавляют проценты, которые рассчитывают исходя из оставшейся части долга. Платежи постепенно уменьшаются: в начале они довольно большие по сравнению с аннуитетными, а в конце — значительно меньше.",
        image="units/5.jpg"
    )

    print("Услуги добавлены")


def add_calculations():
    owners = CustomUser.objects.filter(is_superuser=False)
    moderators = CustomUser.objects.filter(is_superuser=True)

    if len(owners) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    units = Unit.objects.all()

    for _ in range(30):
        calculation = Calculation.objects.create()
        calculation.status = random.randint(2, 5)
        calculation.owner = random.choice(owners)

        if calculation.status in [3, 4]:
            calculation.date_complete = random_date()
            calculation.date_formation = calculation.date_complete - random_timedelta()
            calculation.date_created = calculation.date_formation - random_timedelta()
            calculation.moderator = random.choice(moderators)
        else:
            calculation.date_formation = random_date()
            calculation.date_created = calculation.date_formation - random_timedelta()

        for i in range(random.randint(1, 3)):
            calculation.units.add(random.choice(units))

        calculation.save()

    print("Заявки добавлены")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        management.call_command("clean_db")
        management.call_command("add_users")

        add_units()
        add_calculations()









