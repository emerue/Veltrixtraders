from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import uuid

class User(AbstractUser):
    # Personal Information
    title = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address Information
    house_no = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Profile
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')
    
    # Account Status
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=255, blank=True, null=True)
    is_kyc_verified = models.BooleanField(default=False)
    
    # Notification Preferences
    email_deposit = models.BooleanField(default=True)
    email_withdrawal = models.BooleanField(default=True)
    email_trade = models.BooleanField(default=True)
    email_account_update = models.BooleanField(default=True)
    push_deposit = models.BooleanField(default=True)
    push_withdrawal = models.BooleanField(default=True)
    push_trade = models.BooleanField(default=True)
    
    # KYC Information
    document_type = models.CharField(max_length=20, blank=True, null=True)
    document_number = models.CharField(max_length=100, blank=True, null=True)
    document_expiry = models.DateField(blank=True, null=True)
    document_front = models.ImageField(upload_to='kyc/', blank=True, null=True)
    document_back = models.ImageField(upload_to='kyc/', blank=True, null=True)
    
    # Trading Profile
    yrs_experience = models.CharField(max_length=50, blank=True, null=True)
    trading_frequency = models.CharField(max_length=50, blank=True, null=True)
    instrument_traded = models.TextField(blank=True, null=True)
    knowledge_level = models.CharField(max_length=50, blank=True, null=True)
    preferred_market = models.CharField(max_length=100, blank=True, null=True)
    trading_platform = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial Profile
    annual_income = models.CharField(max_length=50, blank=True, null=True)
    source_of_income = models.CharField(max_length=100, blank=True, null=True)
    tax_residence = models.CharField(max_length=100, blank=True, null=True)
    
    # Balances
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    bonus_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_withdrawal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Add this field to your User model in the Balances section
    loyalty_status = models.CharField(max_length=50, default='Bronze')
    loyalty_tier_color = models.CharField(max_length=20, blank=True, null=True)
    loyalty_benefits = models.TextField(blank=True, null=True)
    loyalty_updated_at = models.DateTimeField(auto_now=True)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace('-', '')[:12].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username


class PaymentMethod(models.Model):
    TYPE_CHOICES = [
        ('crypto', 'Cryptocurrency'),
        ('bank', 'Bank Transfer'),
    ]
    
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT_ERC20', 'USDT (ERC20)'),
        ('USDT_TRC20', 'USDT (TRC20)'),
        ('SOL', 'Solana'),
        ('XRP', 'XRP'),
    ]
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    crypto_symbol = models.CharField(max_length=20, choices=CRYPTO_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    min_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=10)
    max_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=100000)
    min_withdrawal = models.DecimalField(max_digits=20, decimal_places=2, default=10)
    max_withdrawal = models.DecimalField(max_digits=20, decimal_places=2, default=50000)
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_time = models.CharField(max_length=100, default="1-3 business days")
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['method_type', 'name']


class PaymentMethodDetail(models.Model):
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='details')
    
    # Common fields
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    network = models.CharField(max_length=50, blank=True, null=True)
    
    # Bank details
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    routing_number = models.CharField(max_length=100, blank=True, null=True)
    swift_code = models.CharField(max_length=50, blank=True, null=True)
    iban = models.CharField(max_length=100, blank=True, null=True)
    beneficiary_address = models.TextField(blank=True, null=True)
    
    # QR Code
    qr_code = models.ImageField(upload_to='payment_qr/', blank=True, null=True)
    
    # Additional info
    additional_info = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.payment_method.name} Details"


class Deposit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount_usd = models.DecimalField(max_digits=20, decimal_places=2)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    network = models.CharField(max_length=50, blank=True, null=True)
    
    # Proof of payment
    proof_image = models.ImageField(upload_to='deposit_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount_usd} - {self.status}"


class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount_usd = models.DecimalField(max_digits=20, decimal_places=2)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    
    # Withdrawal destination
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    network = models.CharField(max_length=50, blank=True, null=True)
    
    # Bank details for withdrawal
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    routing_number = models.CharField(max_length=100, blank=True, null=True)
    swift_code = models.CharField(max_length=50, blank=True, null=True)
    iban = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"WTH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount_usd} - {self.status}"


class Trader(models.Model):
    RISK_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES)
    specialty = models.CharField(max_length=100)
    monthly_return = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_return = models.DecimalField(max_digits=10, decimal_places=2)
    win_rate = models.DecimalField(max_digits=10, decimal_places=2)
    experience_years = models.IntegerField()
    description = models.TextField(blank=True)
    fee_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    min_investment = models.DecimalField(max_digits=20, decimal_places=2)
    followers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-followers']


class CopyTrade(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('stopped', 'Stopped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='copy_trades')
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.trader.name}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('commission', 'Commission'),
        ('trade', 'Trade'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255, blank=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    
    # For crypto transactions
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    network = models.CharField(max_length=50, blank=True, null=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrer_users')
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_by_user')
    commission_earned = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    successful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    
# Add this to your models.py file, preferably after the User model

class LoyaltyStatus(models.Model):
    """
    Model to define loyalty tiers/levels
    """
    name = models.CharField(max_length=50, unique=True)  # Bronze, Silver, Gold, etc.
    level = models.PositiveIntegerField(unique=True)  # 1, 2, 3, 4, 5
    min_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    max_deposit = models.DecimalField(max_digits=20, decimal_places=2, default=999999)
    color = models.CharField(max_length=20, default='#CD7F32')  # Hex color code
    icon = models.CharField(max_length=100, default='images/loyalty/bronze.svg')  # Path to icon
    
    # Benefits and perks
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Deposit bonus %
    referral_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Referral bonus amount
    direct_referral_required = models.PositiveIntegerField(default=0)  # Direct referrals needed
    referral_deposits_required = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # Referral deposits needed
    
    # Description and benefits
    benefits = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['level']
        verbose_name_plural = "Loyalty Statuses"
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"