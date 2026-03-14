# yourapp/management/commands/add_payment_methods.py

from django.core.management.base import BaseCommand
from VeltrixApp.models import PaymentMethod, PaymentMethodDetail, Currency

class Command(BaseCommand):
    help = 'Adds CashApp and PayPal payment methods'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing payment methods',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Get all active currencies
        currencies = Currency.objects.filter(is_active=True)
        
        if not currencies.exists():
            self.stdout.write(self.style.ERROR('No currencies found. Run create_currencies first.'))
            return
        
        # CashApp payment method
        cashapp, created = PaymentMethod.objects.update_or_create(
            name='CashApp',
            defaults={
                'method_type': 'cashapp',
                'is_active': True,
                'min_deposit': 10,
                'max_deposit': 5000,
                'min_withdrawal': 10,
                'max_withdrawal': 2500,
                'withdrawal_fee': 1.5,
                'processing_time': 'Instant to 24 hours',
                'instructions': 'Send payment to the provided $Cashtag. Include your transaction ID in the payment note.',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created CashApp payment method'))
        else:
            self.stdout.write(self.style.WARNING('↻ Updated CashApp payment method'))
        
        # PayPal payment method
        paypal, created = PaymentMethod.objects.update_or_create(
            name='PayPal',
            defaults={
                'method_type': 'paypal',
                'is_active': True,
                'min_deposit': 10,
                'max_deposit': 10000,
                'min_withdrawal': 10,
                'max_withdrawal': 5000,
                'withdrawal_fee': 2.9,
                'processing_time': 'Instant to 48 hours',
                'instructions': 'Send payment to the provided PayPal email or PayPal.Me link. Use "Friends and Family" option if available.',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created PayPal payment method'))
        else:
            self.stdout.write(self.style.WARNING('↻ Updated PayPal payment method'))
        
        # Create payment details for each currency
        cashapp_details_count = 0
        paypal_details_count = 0
        
        for currency in currencies:
            # CashApp details
            cashapp_detail, cashapp_created = PaymentMethodDetail.objects.update_or_create(
                payment_method=cashapp,
                currency=currency,
                defaults={
                    'cashapp_tag': '$Veltrixtraders',
                    'additional_info': f'Send {currency.code} payment to this $Cashtag. Please include your transaction ID in the payment note.',
                    'is_default': True,
                }
            )
            
            if cashapp_created:
                cashapp_details_count += 1
            
            # PayPal details
            paypal_detail, paypal_created = PaymentMethodDetail.objects.update_or_create(
                payment_method=paypal,
                currency=currency,
                defaults={
                    'paypal_email': 'payments@veltrixtraders.com',
                    'paypal_me_link': 'https://paypal.me/veltrixtraders',
                    'additional_info': f'Send {currency.code} payment to this PayPal email. Please use "Friends and Family" option.',
                    'is_default': True,
                }
            )
            
            if paypal_created:
                paypal_details_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {cashapp_details_count} CashApp currency details'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {paypal_details_count} PayPal currency details'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Payment methods added successfully!'))
        self.stdout.write(f'CashApp: {cashapp}')
        self.stdout.write(f'PayPal: {paypal}')
        self.stdout.write('='*50)