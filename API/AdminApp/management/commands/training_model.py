
from django.core.management.base import BaseCommand
from AdminApp.scripts.forecast_ml_model import train_model_on_weekly_basis

class Command(BaseCommand):
    help = 'Training forecast data'

    def handle(self, *args, **options):
        self.stdout.write('Training forecast data')
        train_model_on_weekly_basis()
        self.stdout.write(self.style.SUCCESS('Trained successfully'))
