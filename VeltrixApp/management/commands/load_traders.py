import VeltrixApp.views
from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
from VeltrixApp.models import Trader

class Command(BaseCommand):
    help = 'Load traders from traders.json file'

    def handle(self, *args, **options):
        json_file_path = os.path.join(settings.BASE_DIR, 'traders.json')
        
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                traders_data = data.get('traders', [])
                
                for trader_data in traders_data:
                    Trader.objects.update_or_create(
                        id=trader_data['id'],
                        defaults={
                            'name': trader_data['name'],
                            'image_url': trader_data['image_url'],
                            'risk_level': trader_data['risk_level'],
                            'specialty': trader_data['specialty'],
                            'monthly_return': trader_data['monthly_return'],
                            'yearly_return': trader_data['yearly_return'],
                            'win_rate': trader_data['win_rate'],
                            'experience_years': trader_data['experience_years'],
                            'description': trader_data.get('description', ''),
                            'fee_percentage': trader_data['fee_percentage'],
                            'min_investment': trader_data['min_investment'],
                            'followers': trader_data['followers'],
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(traders_data)} traders'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('traders.json not found'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON in traders.json'))