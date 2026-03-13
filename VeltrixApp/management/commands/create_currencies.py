# yourapp/management/commands/create_currencies.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from VeltrixApp.models import Currency  # Replace 'yourapp' with your actual app name

class Command(BaseCommand):
    help = 'Creates initial currency records for the payment system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of currencies even if they exist',
        )
        
        parser.add_argument(
            '--activate-all',
            action='store_true',
            help='Activate all currencies (default is True)',
        )
        
        parser.add_argument(
            '--specific',
            nargs='+',
            choices=['USD', 'GBP', 'EUR', 'CZK', 'CNY', 'CAD', 'JPY'],
            help='Create only specific currencies (e.g., --specific USD EUR GBP)',
        )

    def handle(self, *args, **options):
        force = options['force']
        activate_all = options.get('activate_all', True)
        specific_currencies = options.get('specific')
        
        # Define all currencies
        all_currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_active': True},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_active': True},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_active': True},
            {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč', 'is_active': True},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'is_active': True},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'is_active': True},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'is_active': True},
        ]
        
        # Filter currencies if specific ones are requested
        if specific_currencies:
            currencies_to_create = [
                curr for curr in all_currencies 
                if curr['code'] in specific_currencies
            ]
            self.stdout.write(
                self.style.WARNING(
                    f"Creating only specific currencies: {', '.join(specific_currencies)}"
                )
            )
        else:
            currencies_to_create = all_currencies
            self.stdout.write(
                self.style.WARNING("Creating all currencies")
            )
        
        # Count existing currencies
        existing_count = Currency.objects.count()
        
        if existing_count > 0 and not force:
            self.stdout.write(
                self.style.ERROR(
                    f'Currencies already exist ({existing_count} found). '
                    'Use --force to recreate or update them.'
                )
            )
            
            # Show existing currencies
            existing = Currency.objects.all().values_list('code', flat=True)
            self.stdout.write(f'Existing currencies: {", ".join(existing)}')
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        try:
            with transaction.atomic():
                for currency_data in currencies_to_create:
                    code = currency_data['code']
                    
                    # Set activation status based on flag
                    if not activate_all:
                        currency_data['is_active'] = False
                    
                    # Try to get existing currency
                    currency, created = Currency.objects.update_or_create(
                        code=code,
                        defaults={
                            'name': currency_data['name'],
                            'symbol': currency_data['symbol'],
                            'is_active': currency_data['is_active'],
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created currency: {code} - {currency_data["name"]}')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Updated currency: {code} - {currency_data["name"]}')
                        )
                
                # Handle currencies that should be removed if using force
                if force and not specific_currencies:
                    # Get codes we want to keep
                    keep_codes = [c['code'] for c in currencies_to_create]
                    
                    # Delete currencies not in our list
                    deleted = Currency.objects.exclude(code__in=keep_codes).delete()
                    if deleted[0] > 0:
                        self.stdout.write(
                            self.style.WARNING(f'✗ Removed {deleted[0]} currencies not in the standard list')
                        )
                
        except Exception as e:
            raise CommandError(f'Error creating currencies: {str(e)}')
        
        # Final summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Currency creation completed!'))
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        self.stdout.write(f'Skipped: {skipped_count}')
        self.stdout.write('='*50)
        
        # Show all active currencies
        active_currencies = Currency.objects.filter(is_active=True).order_by('code')
        if active_currencies.exists():
            self.stdout.write('\n' + self.style.SUCCESS('Active currencies:'))
            for currency in active_currencies:
                self.stdout.write(f'  • {currency.code} - {currency.name} ({currency.symbol})')


class CommandWithProgress(Command):
    """Alternative version with progress bar for large datasets"""
    
    def handle(self, *args, **options):
        from tqdm import tqdm  # Optional: pip install tqdm for progress bars
        
        force = options['force']
        specific_currencies = options.get('specific')
        
        all_currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_active': True},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_active': True},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_active': True},
            {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč', 'is_active': True},
            {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'is_active': True},
            {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'is_active': True},
            {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'is_active': True},
        ]
        
        if specific_currencies:
            currencies_to_create = [
                curr for curr in all_currencies 
                if curr['code'] in specific_currencies
            ]
        else:
            currencies_to_create = all_currencies
        
        if Currency.objects.exists() and not force:
            self.stdout.write(
                self.style.ERROR('Currencies already exist. Use --force to recreate.')
            )
            return
        
        created = 0
        updated = 0
        
        try:
            for currency_data in tqdm(currencies_to_create, desc="Creating currencies"):
                currency, created_flag = Currency.objects.update_or_create(
                    code=currency_data['code'],
                    defaults={
                        'name': currency_data['name'],
                        'symbol': currency_data['symbol'],
                        'is_active': currency_data['is_active'],
                    }
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
                    
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created} and updated {updated} currencies'
            )
        )