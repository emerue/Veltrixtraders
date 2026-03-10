# management/commands/process_transactions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from VeltrixApp.models import Deposit, Withdrawal
from VeltrixApp.admin_actions import bulk_process_deposits, bulk_process_withdrawals
from datetime import timedelta

class Command(BaseCommand):
    help = 'Process pending transactions and update user balances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['deposit', 'withdrawal', 'all'],
            default='all',
            help='Type of transactions to process'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Process transactions from last N days'
        )
        
        parser.add_argument(
            '--status',
            type=str,
            default='completed',
            help='Status of transactions to process (default: completed)'
        )

    def handle(self, *args, **options):
        transaction_type = options['type']
        days = options['days']
        status = options['status']
        
        # Base queryset filter
        date_filter = {}
        if days:
            cutoff_date = timezone.now() - timedelta(days=days)
            date_filter = {'created_at__gte': cutoff_date}
        
        if transaction_type in ['deposit', 'all']:
            # Process deposits
            deposits = Deposit.objects.filter(
                status=status,
                completed_at__isnull=True,
                **date_filter
            )
            
            deposit_count = deposits.count()
            if deposit_count > 0:
                self.stdout.write(f"Processing {deposit_count} deposits...")
                success, failed = bulk_process_deposits(deposits)
                self.stdout.write(
                    self.style.SUCCESS(f"Deposits: {success} processed, {failed} failed")
                )
            else:
                self.stdout.write("No deposits to process")
        
        if transaction_type in ['withdrawal', 'all']:
            # Process withdrawals
            withdrawals = Withdrawal.objects.filter(
                status=status,
                completed_at__isnull=True,
                **date_filter
            )
            
            withdrawal_count = withdrawals.count()
            if withdrawal_count > 0:
                self.stdout.write(f"Processing {withdrawal_count} withdrawals...")
                success, failed, insufficient = bulk_process_withdrawals(withdrawals)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Withdrawals: {success} processed, {failed} failed "
                        f"({insufficient} insufficient balance)"
                    )
                )
            else:
                self.stdout.write("No withdrawals to process")