# admin_actions.py
from django.utils import timezone
from .models import Deposit, Withdrawal, User, Transaction, Notification, LoyaltyStatus
from .email_utils import (
    send_deposit_status_update_email, 
    send_withdrawal_status_update_email,
    send_deposit_confirmation_email,
    send_withdrawal_confirmation_email
)
from decimal import Decimal
from django.db import transaction

def process_completed_deposit(deposit):
    """Process a single completed deposit"""
    with transaction.atomic():
        user = deposit.user
        
        # Update user balance
        user.balance += deposit.amount_usd
        user.total_deposit += deposit.amount_usd
        user.save()
        
        # Set completed timestamp
        deposit.completed_at = timezone.now()
        deposit.save(update_fields=['completed_at'])
        
        # Create transaction record
        Transaction.objects.get_or_create(
            user=user,
            transaction_type='deposit',
            amount=deposit.amount_usd,
            status='completed',
            reference_id=deposit.transaction_id,
            defaults={
                'description': f'Deposit via {deposit.payment_method.name if deposit.payment_method else "Unknown"}',
                'wallet_address': deposit.wallet_address,
                'network': deposit.network,
            }
        )
        
        # Create notification
        Notification.objects.create(
            user=user,
            title='Deposit Completed',
            message=f'Your deposit of ${deposit.amount_usd} has been completed successfully.',
        )
        
        # Send email
        try:
            send_deposit_status_update_email(deposit)
            print(f"Deposit completion email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send deposit status email: {e}")
        
        # Update loyalty status
        update_loyalty_status(user)
        
        return True

def process_completed_withdrawal(withdrawal):
    """Process a single completed withdrawal"""
    with transaction.atomic():
        user = withdrawal.user
        
        if user.balance >= withdrawal.amount_usd:
            # Update user balance
            user.balance -= withdrawal.amount_usd
            user.total_withdrawal += withdrawal.amount_usd
            user.save()
            
            # Set completed timestamp
            withdrawal.completed_at = timezone.now()
            withdrawal.save(update_fields=['completed_at'])
            
            # Create transaction record
            Transaction.objects.create(
                user=user,
                transaction_type='withdrawal',
                amount=withdrawal.amount_usd,
                status='completed',
                reference_id=withdrawal.transaction_id,
                description=f'Withdrawal via {withdrawal.payment_method.name if withdrawal.payment_method else "Unknown"}',
                wallet_address=withdrawal.wallet_address,
                network=withdrawal.network,
            )
            
            # Create notification
            Notification.objects.create(
                user=user,
                title='Withdrawal Completed',
                message=f'Your withdrawal of ${withdrawal.amount_usd} has been processed successfully.',
            )
            
            # Send email
            try:
                send_withdrawal_status_update_email(withdrawal)
                print(f"Withdrawal completion email sent to {user.email}")
            except Exception as e:
                print(f"Failed to send withdrawal status email: {e}")
            
            return True
        else:
            # Mark as failed if insufficient balance
            withdrawal.status = 'failed'
            withdrawal.save(update_fields=['status'])
            
            Notification.objects.create(
                user=user,
                title='Withdrawal Failed',
                message=f'Your withdrawal of ${withdrawal.amount_usd} failed due to insufficient funds.',
            )
            
            # Send email
            try:
                send_withdrawal_status_update_email(withdrawal)
                print(f"Withdrawal failure email sent to {user.email}")
            except Exception as e:
                print(f"Failed to send withdrawal status email: {e}")
            
            return False

def process_failed_deposit(deposit, reason=None):
    """Mark a deposit as failed and notify user"""
    with transaction.atomic():
        deposit.status = 'failed'
        if reason:
            deposit.notes = reason
        deposit.save()
        
        # Create notification
        Notification.objects.create(
            user=deposit.user,
            title='Deposit Failed',
            message=f'Your deposit of ${deposit.amount_usd} has failed. {"Reason: " + reason if reason else "Please contact support."}',
        )
        
        # Send email
        try:
            send_deposit_status_update_email(deposit)
        except Exception as e:
            print(f"Failed to send deposit status email: {e}")

def process_failed_withdrawal(withdrawal, reason=None):
    """Mark a withdrawal as failed and notify user"""
    with transaction.atomic():
        withdrawal.status = 'failed'
        withdrawal.save()
        
        # Create notification
        Notification.objects.create(
            user=withdrawal.user,
            title='Withdrawal Failed',
            message=f'Your withdrawal of ${withdrawal.amount_usd} has failed. {"Reason: " + reason if reason else "Please contact support."}',
        )
        
        # Send email
        try:
            send_withdrawal_status_update_email(withdrawal)
        except Exception as e:
            print(f"Failed to send withdrawal status email: {e}")

def update_loyalty_status(user):
    """Update user loyalty status based on total deposits"""
    try:
        # Get all loyalty tiers
        loyalty_tiers = LoyaltyStatus.objects.filter(is_active=True).order_by('level')
        
        if loyalty_tiers.exists():
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
                
                # Create notification for loyalty upgrade
                Notification.objects.create(
                    user=user,
                    title='Loyalty Status Upgraded',
                    message=f'Congratulations! Your loyalty status has been upgraded to {current_tier.name}.',
                )
    except Exception as e:
        print(f"Error updating loyalty status for user {user.id}: {e}")

def bulk_process_deposits(deposit_queryset):
    """Bulk process multiple deposits"""
    success_count = 0
    failed_count = 0
    
    for deposit in deposit_queryset:
        try:
            if deposit.status == 'completed' and not deposit.completed_at:
                if process_completed_deposit(deposit):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Error processing deposit {deposit.id}: {str(e)}")
    
    return success_count, failed_count

def bulk_process_withdrawals(withdrawal_queryset):
    """Bulk process multiple withdrawals"""
    success_count = 0
    failed_count = 0
    insufficient_balance_count = 0
    
    for withdrawal in withdrawal_queryset:
        try:
            if withdrawal.status == 'completed' and not withdrawal.completed_at:
                success = process_completed_withdrawal(withdrawal)
                if success:
                    success_count += 1
                else:
                    insufficient_balance_count += 1
                    failed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Error processing withdrawal {withdrawal.id}: {str(e)}")
    
    return success_count, failed_count, insufficient_balance_count

def resend_transaction_emails(queryset, transaction_type):
    """Resend status emails for transactions"""
    sent_count = 0
    failed_count = 0
    
    for item in queryset:
        try:
            if transaction_type == 'deposit':
                send_deposit_status_update_email(item)
            else:
                send_withdrawal_status_update_email(item)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to resend email for {transaction_type} {item.id}: {e}")
    
    return sent_count, failed_count