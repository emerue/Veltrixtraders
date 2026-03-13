# yourapp/management/commands/create_payment_details.py

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction
from VeltrixApp.models import PaymentMethod, Currency, PaymentMethodDetail
import random
import string
from decimal import Decimal

class Command(BaseCommand):
    help = 'Creates mock payment details for payment methods and currencies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate payment details even if they exist',
        )
        
        parser.add_argument(
            '--method',
            type=str,
            help='Create details for specific payment method (by name)',
        )
        
        parser.add_argument(
            '--currency',
            type=str,
            help='Create details for specific currency (by code)',
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing payment details before creating new ones',
        )

    def generate_wallet_address(self, crypto_type):
        """Generate mock wallet addresses based on crypto type"""
        prefixes = {
            'BTC': ['1', '3', 'bc1'],
            'ETH': ['0x'],
            'USDT_ERC20': ['0x'],
            'USDT_TRC20': ['T'],
            'SOL': ['SOL'],
            'XRP': ['r'],
        }
        
        prefix = prefixes.get(crypto_type, ['0x'])[0]
        # Generate random string of 30-40 chars
        chars = string.ascii_letters + string.digits
        address_length = random.randint(30, 40)
        random_part = ''.join(random.choice(chars) for _ in range(address_length))
        
        return f"{prefix}{random_part}"

    def generate_iban(self, country_code='GB'):
        """Generate mock IBAN"""
        # Format: 2 letters country code + 2 check digits + up to 30 alphanumeric chars
        country = country_code.upper()
        check_digits = str(random.randint(10, 99))
        bank_code = ''.join(random.choice(string.digits) for _ in range(4))
        account_number = ''.join(random.choice(string.digits) for _ in range(16))
        
        return f"{country}{check_digits}{bank_code}{account_number}"

    def generate_account_number(self):
        """Generate mock account number"""
        return ''.join(random.choice(string.digits) for _ in range(10))

    def generate_routing_number(self):
        """Generate mock routing number (9 digits for US)"""
        return ''.join(random.choice(string.digits) for _ in range(9))

    def generate_swift_code(self, bank_name):
        """Generate mock SWIFT code based on bank name"""
        # Format: 4 letters bank code + 2 letters country code + 2 letters location code + 3 optional
        bank_prefix = bank_name[:4].upper() if len(bank_name) >= 4 else bank_name.upper().ljust(4, 'X')
        country = 'US'
        location = 'NY'
        return f"{bank_prefix}{country}{location}XXX"

    def handle(self, *args, **options):
        force = options['force']
        method_filter = options.get('method')
        currency_filter = options.get('currency')
        clear_existing = options.get('clear')
        
        # Clear existing details if requested
        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing payment details...'))
            PaymentMethodDetail.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ All payment details cleared'))
        
        # Get payment methods
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        if method_filter:
            payment_methods = payment_methods.filter(name__icontains=method_filter)
        
        if not payment_methods.exists():
            self.stdout.write(self.style.ERROR('No payment methods found. Create payment methods first.'))
            return
        
        # Get currencies
        currencies = Currency.objects.filter(is_active=True)
        if currency_filter:
            currencies = currencies.filter(code=currency_filter)
        
        if not currencies.exists():
            self.stdout.write(self.style.ERROR('No currencies found. Run create_currencies command first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {payment_methods.count()} payment methods and {currencies.count()} currencies'))
        
        # Mock bank names by region
        bank_names = {
            'USD': ['Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank', 'US Bank'],
            'GBP': ['Barclays', 'HSBC UK', 'Lloyds Bank', 'NatWest', 'Santander UK'],
            'EUR': ['Deutsche Bank', 'BNP Paribas', 'Santander', 'UniCredit', 'ING Group'],
            'CZK': ['Česká spořitelna', 'ČSOB', 'Komerční banka', 'Raiffeisenbank', 'Moneta Money Bank'],
            'CNY': ['Industrial and Commercial Bank of China', 'China Construction Bank', 'Bank of China', 'Agricultural Bank of China'],
            'CAD': ['Royal Bank of Canada', 'TD Bank', 'Scotiabank', 'BMO', 'CIBC'],
            'JPY': ['Mitsubishi UFJ Financial Group', 'Sumitomo Mitsui Financial Group', 'Mizuho Financial Group'],
        }
        
        # Account names
        account_names = [
            'Veltrixtraders Ltd',
            'Veltrixtraders Holdings',
            'Veltrixtraders Financial',
            'Veltrixtraders Trading',
            'Veltrixtraders Investments',
        ]
        
        created_count = 0
        updated_count = 0
        
        try:
            with transaction.atomic():
                for payment_method in payment_methods:
                    self.stdout.write(f'\nProcessing: {payment_method.name}')
                    
                    for currency in currencies:
                        # Check if details already exist
                        existing = PaymentMethodDetail.objects.filter(
                            payment_method=payment_method,
                            currency=currency
                        ).first()
                        
                        if existing and not force and not clear_existing:
                            self.stdout.write(
                                self.style.WARNING(f'  ↻ Skipping {currency.code} (already exists)')
                            )
                            continue
                        
                        # Create or update details based on method type
                        if payment_method.method_type == 'crypto':
                            details, created = self.create_crypto_details(
                                payment_method, currency, account_names
                            )
                        else:  # bank
                            details, created = self.create_bank_details(
                                payment_method, currency, account_names, bank_names
                            )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ Created {currency.code} details')
                            )
                        else:
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'  ↻ Updated {currency.code} details')
                            )
                    
                    # Create fallback details (no currency) if they don't exist
                    fallback, fallback_created = PaymentMethodDetail.objects.update_or_create(
                        payment_method=payment_method,
                        currency=None,
                        defaults={
                            'additional_info': 'Contact support for specific currency payment details.',
                            'is_default': False,
                        }
                    )
                    
                    if fallback_created:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ Created fallback details (no currency)')
                        )
                
        except Exception as e:
            raise CommandError(f'Error creating payment details: {str(e)}')
        
        # Final summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Payment details creation completed!'))
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        self.stdout.write('='*60)
        
        # Show summary by method
        self.stdout.write('\n' + self.style.SUCCESS('Summary by payment method:'))
        for method in payment_methods:
            details_count = PaymentMethodDetail.objects.filter(payment_method=method).count()
            self.stdout.write(f'  • {method.name}: {details_count} detail records')

    def create_crypto_details(self, payment_method, currency, account_names):
        """Create crypto payment details"""
        crypto_symbol = payment_method.crypto_symbol
        
        # Generate wallet address
        wallet_address = self.generate_wallet_address(crypto_symbol)
        
        # Determine network based on crypto symbol
        network_map = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum (ERC20)',
            'USDT_ERC20': 'Ethereum (ERC20)',
            'USDT_TRC20': 'Tron (TRC20)',
            'SOL': 'Solana',
            'XRP': 'XRP Ledger',
        }
        
        network = network_map.get(crypto_symbol, 'Mainnet')
        
        # Generate additional info
        additional_info = (
            f"Minimum confirmation: 3 blocks\n"
            f"Processing time: 10-30 minutes\n"
            f"Network fee: 0.0001 {crypto_symbol}"
        )
        
        # Create or update
        details, created = PaymentMethodDetail.objects.update_or_create(
            payment_method=payment_method,
            currency=currency,
            defaults={
                'wallet_address': wallet_address,
                'network': network,
                'additional_info': additional_info,
                'is_default': True,
                'currency_specific_instructions': (
                    f"This address accepts {currency.code} payments via {currency.name}. "
                    f"Please ensure you're sending from a compatible wallet."
                ),
            }
        )
        
        return details, created

    def create_bank_details(self, payment_method, currency, account_names, bank_names):
        """Create bank payment details"""
        # Get bank names for this currency
        currency_banks = bank_names.get(currency.code, bank_names['USD'])
        bank_name = random.choice(currency_banks)
        
        # Generate account details
        account_name = random.choice(account_names)
        account_number = self.generate_account_number()
        
        # Generate routing number or sort code based on currency
        if currency.code in ['GBP', 'EUR']:
            # UK sort code format: XX-XX-XX
            routing_number = f"{random.randint(10,99)}-{random.randint(10,99)}-{random.randint(10,99)}"
        else:
            routing_number = self.generate_routing_number()
        
        # Generate SWIFT code
        swift_code = self.generate_swift_code(bank_name)
        
        # Generate IBAN for certain currencies
        iban = None
        if currency.code in ['EUR', 'GBP', 'CZK']:
            country_map = {'GBP': 'GB', 'EUR': 'DE', 'CZK': 'CZ'}
            country = country_map.get(currency.code, 'GB')
            iban = self.generate_iban(country)
        
        # Currency-specific instructions
        instructions_map = {
            'USD': "For USD wire transfers, include 'Veltrixtraders' in the reference field.",
            'GBP': "For GBP faster payments, use the sort code and account number provided.",
            'EUR': "For SEPA transfers, use the IBAN and SWIFT code provided.",
            'CZK': "For domestic CZK transfers, use the account number and bank code.",
            'CNY': "International transfers may require additional processing time.",
            'CAD': "For CAD EFT transfers, use the transit number and institution number.",
            'JPY': "International wire transfers may take 2-3 business days.",
        }
        
        currency_specific_instructions = instructions_map.get(
            currency.code, 
            f"Please include your transaction ID ({payment_method.name}) in the payment reference."
        )
        
        # Beneficiary address
        beneficiary_address = "123 Financial District, London, EC2V 6DN, United Kingdom"
        
        # Additional info
        additional_info = (
            f"Bank: {bank_name}\n"
            f"Processing time: {payment_method.processing_time}\n"
            f"Please upload proof of payment after transfer."
        )
        
        # Create or update
        details, created = PaymentMethodDetail.objects.update_or_create(
            payment_method=payment_method,
            currency=currency,
            defaults={
                'bank_name': bank_name,
                'account_name': account_name,
                'account_number': account_number,
                'routing_number': routing_number,
                'swift_code': swift_code,
                'iban': iban,
                'beneficiary_address': beneficiary_address,
                'currency_specific_instructions': currency_specific_instructions,
                'additional_info': additional_info,
                'is_default': True,
            }
        )
        
        return details, created