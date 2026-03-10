from django.core.management.base import BaseCommand
from VeltrixApp.models import PaymentMethod, PaymentMethodDetail

class Command(BaseCommand):
    help = 'Create initial payment methods'

    def handle(self, *args, **options):
        # Crypto methods
        btc, _ = PaymentMethod.objects.get_or_create(
            name='Bitcoin',
            method_type='crypto',
            crypto_symbol='BTC',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 0.0001,
                'processing_time': '1-3 business hours',
                'instructions': 'Send Bitcoin to the wallet address provided. Make sure to use the BTC network.',
            }
        )
        
        eth, _ = PaymentMethod.objects.get_or_create(
            name='Ethereum',
            method_type='crypto',
            crypto_symbol='ETH',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 0.001,
                'processing_time': '1-3 business hours',
                'instructions': 'Send Ethereum to the wallet address provided. Make sure to use the ETH network.',
            }
        )
        
        usdt_erc20, _ = PaymentMethod.objects.get_or_create(
            name='USDT (ERC20)',
            method_type='crypto',
            crypto_symbol='USDT',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 1.0,
                'processing_time': '1-3 business hours',
                'instructions': 'Send USDT to the wallet address provided. Make sure to use the ERC20 network.',
            }
        )
        
        usdt_trc20, _ = PaymentMethod.objects.get_or_create(
            name='USDT (TRC20)',
            method_type='crypto',
            crypto_symbol='USDT',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 0.5,
                'processing_time': '1-3 business hours',
                'instructions': 'Send USDT to the wallet address provided. Make sure to use the TRC20 network.',
            }
        )
        
        sol, _ = PaymentMethod.objects.get_or_create(
            name='Solana',
            method_type='crypto',
            crypto_symbol='SOL',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 0.001,
                'processing_time': '1-3 business hours',
                'instructions': 'Send Solana to the wallet address provided. Make sure to use the SOL network.',
            }
        )
        
        xrp, _ = PaymentMethod.objects.get_or_create(
            name='XRP',
            method_type='crypto',
            crypto_symbol='XRP',
            defaults={
                'min_deposit': 10,
                'max_deposit': 100000,
                'min_withdrawal': 10,
                'max_withdrawal': 50000,
                'withdrawal_fee': 0.1,
                'processing_time': '1-3 business hours',
                'instructions': 'Send XRP to the wallet address provided. Make sure to include the destination tag if required.',
            }
        )
        
        # Bank method
        bank, _ = PaymentMethod.objects.get_or_create(
            name='Bank Transfer',
            method_type='bank',
            defaults={
                'min_deposit': 100,
                'max_deposit': 1000000,
                'min_withdrawal': 100,
                'max_withdrawal': 500000,
                'withdrawal_fee': 0,
                'processing_time': '1-3 business days',
                'instructions': 'Transfer the amount to the bank account details provided. Please use your transaction ID as reference.',
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created payment methods'))