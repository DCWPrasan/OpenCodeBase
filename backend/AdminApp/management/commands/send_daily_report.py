
from django.core.management.base import BaseCommand
from AdminApp.helper import send_daily_stock_report_mail

class Command(BaseCommand):
    help = 'Training forecast data'

    def handle(self, *args, **options):
        self.stdout.write('Sending Daily Stock Report')
        send_daily_stock_report_mail()
        self.stdout.write(self.style.SUCCESS('Daily Stock Report Mail Sent successfully'))
