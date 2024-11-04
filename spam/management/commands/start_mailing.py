from django.core.management.base import BaseCommand
from spam.models import Mailing


class Command(BaseCommand):
    help = "Начать рассылку"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Mailing with id {mailing_id} not found."))
            return

        if mailing.status != "Создана":
            self.stderr.write(self.style.ERROR(f'Mailing with id {mailing_id} is not in "Создана" status.'))
            return

        mailing.send_mailing()
        self.stdout.write(self.style.SUCCESS(f"Mailing with id {mailing_id} started."))
