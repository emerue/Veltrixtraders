from django.core.management.base import BaseCommand
from VeltrixApp.models import PaymentMethod, PaymentMethodDetail, User, LoyaltyStatus
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create initial payment method details and loyalty status'

    def handle(self, *args, **options):
        # Create Payment Method Details for existing payment methods
        self.create_payment_method_details()
        
        # Create Loyalty Status tiers
        self.create_loyalty_tiers()
        
        # Update user loyalty status
        self.update_user_loyalty_status()
        
        self.stdout.write(self.style.SUCCESS('Successfully created payment method details and updated loyalty status'))
    
    def create_payment_method_details(self):
        """Create default payment method details for each payment method"""
        
        # Bitcoin details
        btc = PaymentMethod.objects.filter(crypto_symbol='BTC').first()
        if btc:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=btc,
                defaults={
                    'wallet_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                    'network': 'BTC',
                    'additional_info': 'Bitcoin network (BTC) - Please ensure you are sending from your own wallet',
                    'is_default': True
                }
            )
        
        # Ethereum details
        eth = PaymentMethod.objects.filter(crypto_symbol='ETH').first()
        if eth:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=eth,
                defaults={
                    'wallet_address': '0x742d35Cc6634C0532925a3b844Bc5e7dD3C3e5a8',
                    'network': 'ERC20',
                    'additional_info': 'Ethereum network (ERC20) - Please ensure you are sending from your own wallet',
                    'is_default': True
                }
            )
        
        # USDT ERC20 details
        usdt_erc20 = PaymentMethod.objects.filter(name='USDT (ERC20)').first()
        if usdt_erc20:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=usdt_erc20,
                defaults={
                    'wallet_address': '0x742d35Cc6634C0532925a3b844Bc5e7dD3C3e5a8',
                    'network': 'ERC20',
                    'additional_info': 'USDT on Ethereum network (ERC20) - Please ensure you are sending from your own wallet',
                    'is_default': True
                }
            )
        
        # USDT TRC20 details
        usdt_trc20 = PaymentMethod.objects.filter(name='USDT (TRC20)').first()
        if usdt_trc20:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=usdt_trc20,
                defaults={
                    'wallet_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
                    'network': 'TRC20',
                    'additional_info': 'USDT on TRON network (TRC20) - Please ensure you are sending from your own wallet',
                    'is_default': True
                }
            )
        
        # Solana details
        sol = PaymentMethod.objects.filter(crypto_symbol='SOL').first()
        if sol:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=sol,
                defaults={
                    'wallet_address': '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin',
                    'network': 'SOL',
                    'additional_info': 'Solana network - Please ensure you are sending from your own wallet',
                    'is_default': True
                }
            )
        
        # XRP details
        xrp = PaymentMethod.objects.filter(crypto_symbol='XRP').first()
        if xrp:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=xrp,
                defaults={
                    'wallet_address': 'rLHzPsX6oXkzU2qL12kHCH8G8cnZv1rBJh',
                    'network': 'XRP',
                    'additional_info': 'XRP network - Please include destination tag: 123456789 if required',
                    'is_default': True
                }
            )
        
        # Bank Transfer details
        bank = PaymentMethod.objects.filter(method_type='bank').first()
        if bank:
            PaymentMethodDetail.objects.get_or_create(
                payment_method=bank,
                defaults={
                    'bank_name': 'Global Bank International',
                    'account_name': 'Trading Platform Ltd',
                    'account_number': '1234567890',
                    'routing_number': '021000021',
                    'swift_code': 'GBIUS33',
                    'iban': 'GB33BUKB20201555555555',
                    'beneficiary_address': '123 Financial District, New York, NY 10005, USA',
                    'additional_info': 'Please include your username as reference when making the transfer',
                    'is_default': True
                }
            )
    
    def create_loyalty_tiers(self):
        """Create loyalty status tiers"""
        
        loyalty_tiers = [
            {
                'name': 'Bronze',
                'level': 1,
                'min_deposit': 0,
                'max_deposit': 999,
                'color': '#CD7F32',
                'icon': 'images/loyalty/bronze.svg',
                'bonus_percentage': 0,
                'referral_bonus': 10,
                'direct_referral_required': 0,
                'referral_deposits_required': 0,
                'benefits': 'Basic support, Standard withdrawal limits',
                'description': 'Entry level loyalty tier for new traders'
            },
            {
                'name': 'Silver',
                'level': 2,
                'min_deposit': 1000,
                'max_deposit': 9999,
                'color': '#C0C0C0',
                'icon': 'images/loyalty/silver.svg',
                'bonus_percentage': 2,
                'referral_bonus': 25,
                'direct_referral_required': 1,
                'referral_deposits_required': 1000,
                'benefits': 'Priority support, Reduced fees, Monthly webinars',
                'description': 'Silver tier traders enjoy priority support and reduced fees'
            },
            {
                'name': 'Gold',
                'level': 3,
                'min_deposit': 10000,
                'max_deposit': 49999,
                'color': '#FFD700',
                'icon': 'images/loyalty/gold.svg',
                'bonus_percentage': 5,
                'referral_bonus': 50,
                'direct_referral_required': 3,
                'referral_deposits_required': 5000,
                'benefits': 'VIP support, Lowest fees, Exclusive market insights, Quarterly events',
                'description': 'Gold tier unlocks VIP support and exclusive market insights'
            },
            {
                'name': 'Platinum',
                'level': 4,
                'min_deposit': 50000,
                'max_deposit': 99999,
                'color': '#E5E4E2',
                'icon': 'images/loyalty/platinum.svg',
                'bonus_percentage': 8,
                'referral_bonus': 100,
                'direct_referral_required': 5,
                'referral_deposits_required': 10000,
                'benefits': '24/7 dedicated account manager, Zero fees, Private trading sessions',
                'description': 'Platinum tier features a dedicated account manager and zero fees'
            },
            {
                'name': 'Diamond',
                'level': 5,
                'min_deposit': 100000,
                'max_deposit': 999999999,
                'color': '#B9F2FF',
                'icon': 'images/loyalty/diamond.svg',
                'bonus_percentage': 12,
                'referral_bonus': 200,
                'direct_referral_required': 10,
                'referral_deposits_required': 50000,
                'benefits': 'All Platinum benefits + Profit sharing, Exclusive investment opportunities',
                'description': 'Diamond tier offers profit sharing and exclusive investment opportunities'
            },
        ]
        
        created_count = 0
        for tier_data in loyalty_tiers:
            tier, created = LoyaltyStatus.objects.get_or_create(
                level=tier_data['level'],
                defaults=tier_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created {tier.name} loyalty tier")
            else:
                # Update existing tier
                for key, value in tier_data.items():
                    setattr(tier, key, value)
                tier.save()
                self.stdout.write(f"Updated {tier.name} loyalty tier")
        
        self.stdout.write(self.style.SUCCESS(f'Created/Updated {created_count} loyalty tiers'))
    
    def update_user_loyalty_status(self):
        """Update loyalty status for all users based on their total deposits"""
        
        # Get all loyalty tiers
        loyalty_tiers = LoyaltyStatus.objects.filter(is_active=True).order_by('level')
        
        if not loyalty_tiers.exists():
            self.stdout.write(self.style.WARNING('No loyalty tiers found. Please run create_loyalty_tiers first.'))
            return
        
        # Update each user's loyalty status
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            total_deposits = user.total_deposit or 0
            
            # Determine loyalty tier based on total deposits
            current_tier = loyalty_tiers.first()  # Default to lowest tier
            
            for tier in loyalty_tiers:
                if tier.min_deposit <= total_deposits <= tier.max_deposit:
                    current_tier = tier
                    break
                elif total_deposits > tier.max_deposit:
                    continue
            
            # Update user's loyalty status fields
            if user.loyalty_status != current_tier.name:
                user.loyalty_status = current_tier.name
                user.loyalty_tier_color = current_tier.color
                user.loyalty_benefits = current_tier.benefits
                user.save()
                updated_count += 1
                self.stdout.write(f"Updated {user.username}: {current_tier.name} (${total_deposits})")
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} users with loyalty status'))