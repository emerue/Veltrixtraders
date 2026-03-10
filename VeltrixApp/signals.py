# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Deposit, Withdrawal, User, Transaction, Notification, LoyaltyStatus
from .email_utils import (
    send_deposit_status_update_email, 
    send_withdrawal_status_update_email,
    send_deposit_confirmation_email,
    send_withdrawal_confirmation_email
)
from decimal import Decimal

@receiver(pre_save, sender=Deposit)
def track_deposit_status_change(sender, instance, **kwargs):
    """Track when deposit status changes"""
    if instance.pk:  # If instance already exists
        try:
            old_instance = Deposit.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Deposit.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Deposit)
def update_user_balance_on_deposit_completion(sender, instance, created, **kwargs):
    """Update user balance when deposit is marked as completed"""
    
    # Send confirmation email for new deposits
    if created and instance.status == 'pending':
        try:
            send_deposit_confirmation_email(instance)
            print(f"Deposit confirmation email sent to {instance.user.email}")
        except Exception as e:
            print(f"Failed to send deposit confirmation email: {e}")
    
    # Check if status changed
    if hasattr(instance, '_old_status'):
        old_status = instance._old_status
    else:
        old_status = None
    
    # If status changed (not a new creation with same status)
    if old_status != instance.status:
        
        # Send status update email for significant status changes
        try:
            if instance.status in ['completed', 'failed', 'processing', 'cancelled']:
                send_deposit_status_update_email(instance, old_status)
                print(f"Deposit status email sent to {instance.user.email} for status: {instance.status}")
        except Exception as e:
            print(f"Failed to send deposit status email: {e}")
        
        # If status is now 'completed' and it wasn't before
        if instance.status == 'completed' and old_status != 'completed':
            
            # Update user balance
            user = instance.user
            user.balance += instance.amount_usd
            user.total_deposit += instance.amount_usd
            user.save()
            
            # Set completed timestamp if not set
            if not instance.completed_at:
                instance.completed_at = timezone.now()
                instance.save(update_fields=['completed_at'])
            
            # Create transaction record
            Transaction.objects.get_or_create(
                user=user,
                transaction_type='deposit',
                amount=instance.amount_usd,
                status='completed',
                reference_id=instance.transaction_id,
                defaults={
                    'description': f'Deposit via {instance.payment_method.name if instance.payment_method else "Unknown"}',
                    'wallet_address': instance.wallet_address,
                    'network': instance.network,
                }
            )
            
            # Create notification for user
            Notification.objects.create(
                user=user,
                title='Deposit Completed',
                message=f'Your deposit of ${instance.amount_usd} has been completed successfully.',
            )
            
            # Update loyalty status after deposit
            update_loyalty_status(user)
        
        # If status changed from 'completed' to something else (admin correction)
        elif old_status == 'completed' and instance.status != 'completed':
            # Reverse the balance update
            user = instance.user
            user.balance -= instance.amount_usd
            user.total_deposit -= instance.amount_usd
            user.save()
            
            # Update transaction status
            Transaction.objects.filter(
                user=user,
                reference_id=instance.transaction_id,
                transaction_type='deposit'
            ).update(status=instance.status)
            
            # Create notification
            Notification.objects.create(
                user=user,
                title=f'Deposit {instance.status.title()}',
                message=f'Your deposit of ${instance.amount_usd} has been marked as {instance.status}.',
            )
            
            # Update loyalty status after reversal
            update_loyalty_status(user)
        
        # If status changed to failed
        elif instance.status == 'failed' and old_status != 'failed':
            Notification.objects.create(
                user=instance.user,
                title='Deposit Failed',
                message=f'Your deposit of ${instance.amount_usd} has failed. Please contact support if you have questions.',
            )


@receiver(pre_save, sender=Withdrawal)
def track_withdrawal_status_change(sender, instance, **kwargs):
    """Track when withdrawal status changes"""
    if instance.pk:  # If instance already exists
        try:
            old_instance = Withdrawal.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_amount = old_instance.amount_usd
        except Withdrawal.DoesNotExist:
            instance._old_status = None
            instance._old_amount = None
    else:
        instance._old_status = None
        instance._old_amount = None

@receiver(post_save, sender=Withdrawal)
def update_user_balance_on_withdrawal_completion(sender, instance, created, **kwargs):
    """Update user balance when withdrawal is marked as completed"""
    
    # Send confirmation email for new withdrawals
    if created and instance.status == 'pending':
        try:
            send_withdrawal_confirmation_email(instance)
            print(f"Withdrawal confirmation email sent to {instance.user.email}")
        except Exception as e:
            print(f"Failed to send withdrawal confirmation email: {e}")
    
    # Check if status changed
    if hasattr(instance, '_old_status'):
        old_status = instance._old_status
    else:
        old_status = None
    
    # If status changed (not a new creation with same status)
    if old_status != instance.status:
        
        # Send status update email for significant status changes
        try:
            if instance.status in ['completed', 'failed', 'processing', 'cancelled']:
                send_withdrawal_status_update_email(instance, old_status)
                print(f"Withdrawal status email sent to {instance.user.email} for status: {instance.status}")
        except Exception as e:
            print(f"Failed to send withdrawal status email: {e}")
        
        # If status is now 'completed' and it wasn't before
        if instance.status == 'completed' and old_status != 'completed':
            
            # Update user balance
            user = instance.user
            if user.balance >= instance.amount_usd:
                user.balance -= instance.amount_usd
                user.total_withdrawal += instance.amount_usd
                user.save()
                
                # Set completed timestamp if not set
                if not instance.completed_at:
                    instance.completed_at = timezone.now()
                    instance.save(update_fields=['completed_at'])
                
                # Create transaction record
                Transaction.objects.create(
                    user=user,
                    transaction_type='withdrawal',
                    amount=instance.amount_usd,
                    status='completed',
                    reference_id=instance.transaction_id,
                    description=f'Withdrawal via {instance.payment_method.name if instance.payment_method else "Unknown"}',
                    wallet_address=instance.wallet_address,
                    network=instance.network,
                )
                
                # Create notification for user
                Notification.objects.create(
                    user=user,
                    title='Withdrawal Completed',
                    message=f'Your withdrawal of ${instance.amount_usd} has been processed successfully.',
                )
            else:
                # Insufficient balance - mark as failed
                instance.status = 'failed'
                instance.save(update_fields=['status'])
                
                Notification.objects.create(
                    user=user,
                    title='Withdrawal Failed',
                    message=f'Your withdrawal of ${instance.amount_usd} failed due to insufficient funds.',
                )
        
        # If status changed from 'completed' to something else (admin correction)
        elif old_status == 'completed' and instance.status != 'completed':
            # Reverse the balance update
            user = instance.user
            user.balance += instance.amount_usd
            user.total_withdrawal -= instance.amount_usd
            user.save()
            
            # Update transaction status
            Transaction.objects.filter(
                user=user,
                reference_id=instance.transaction_id,
                transaction_type='withdrawal'
            ).update(status=instance.status)
            
            # Create notification
            Notification.objects.create(
                user=user,
                title=f'Withdrawal {instance.status.title()}',
                message=f'Your withdrawal of ${instance.amount_usd} has been marked as {instance.status}.',
            )
        
        # If status changed to failed
        elif instance.status == 'failed' and old_status != 'failed':
            Notification.objects.create(
                user=instance.user,
                title='Withdrawal Failed',
                message=f'Your withdrawal of ${instance.amount_usd} has failed. Please contact support if you have questions.',
            )


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
                old_status = user.loyalty_status
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
                
                # You could also send an email for loyalty upgrade
                # send_loyalty_upgrade_email(user, old_status, current_tier.name)
    except Exception as e:
        print(f"Error updating loyalty status for user {user.id}: {e}")


# Connect signals for loyalty status update on deposit/withdrawal
@receiver(post_save, sender=Deposit)
@receiver(post_save, sender=Withdrawal)
def update_user_loyalty_status_on_transaction(sender, instance, **kwargs):
    """Update user loyalty status when a transaction is completed"""
    if instance.status == 'completed':
        update_loyalty_status(instance.user)