from django.contrib import admin
from .models import User, PaymentMethod, PaymentMethodDetail, Deposit, Withdrawal, CopyTrade, LoyaltyStatus 

# admin.py
from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from .models import (
    User, PaymentMethod, PaymentMethodDetail, Deposit, Withdrawal,
    Trader, CopyTrade, Transaction, Referral, LoginHistory, Notification,
    LoyaltyStatus
)
from .admin_actions import (
    process_completed_deposit, process_completed_withdrawal,
    process_failed_deposit, process_failed_withdrawal,
    bulk_process_deposits, bulk_process_withdrawals,
    resend_transaction_emails
)

class DepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_usd', 'status', 'created_at', 'completed_at', 'email_sent_status']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id', 'user__email']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    actions = [
        'mark_as_completed', 'mark_as_failed', 'mark_as_processing',
        'process_selected', 'resend_status_emails'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'payment_method')
        }),
        ('Amount Details', {
            'fields': ('amount_usd', 'crypto_amount')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'wallet_address', 'network', 'proof_image', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'created_at', 'updated_at')
        }),
    )
    
    def email_sent_status(self, obj):
        """Display if email was sent (you might want to add a field to track this)"""
        return "✅" if hasattr(obj, 'email_sent') and obj.email_sent else "❌"
    email_sent_status.short_description = "Email"
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        errors = 0
        
        for deposit in queryset:
            if deposit.status != 'completed':
                try:
                    with transaction.atomic():
                        deposit.status = 'completed'
                        deposit.save()
                        
                        # Process the deposit
                        if process_completed_deposit(deposit):
                            updated += 1
                        else:
                            errors += 1
                except Exception as e:
                    errors += 1
                    self.message_user(
                        request, 
                        f"Error processing deposit {deposit.id}: {str(e)}", 
                        level=messages.ERROR
                    )
        
        if updated > 0:
            self.message_user(
                request, 
                f"{updated} deposits marked as completed and processed. Emails sent.", 
                level=messages.SUCCESS
            )
        if errors > 0:
            self.message_user(
                request, 
                f"{errors} deposits failed to process.", 
                level=messages.WARNING
            )
    
    mark_as_completed.short_description = "Mark selected as completed and process (with email)"
    
    def mark_as_failed(self, request, queryset):
        updated = 0
        for deposit in queryset:
            process_failed_deposit(deposit, "Marked as failed by admin")
            updated += 1
        
        self.message_user(
            request, 
            f"{updated} deposits marked as failed. Notification emails sent.", 
            level=messages.SUCCESS
        )
    
    mark_as_failed.short_description = "Mark selected as failed (with email)"
    
    def mark_as_processing(self, request, queryset):
        updated = 0
        for deposit in queryset:
            deposit.status = 'processing'
            deposit.save()
            
            # Send processing email
            from .email_utils import send_deposit_status_update_email
            try:
                send_deposit_status_update_email(deposit)
            except:
                pass
            
            updated += 1
        
        self.message_user(
            request, 
            f"{updated} deposits marked as processing. Status emails sent.", 
            level=messages.SUCCESS
        )
    
    mark_as_processing.short_description = "Mark selected as processing (with email)"
    
    def process_selected(self, request, queryset):
        """Process selected deposits without changing status"""
        processed = 0
        errors = 0
        
        for deposit in queryset.filter(status='completed', completed_at__isnull=True):
            try:
                if process_completed_deposit(deposit):
                    processed += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
        
        self.message_user(
            request, 
            f"{processed} deposits processed successfully, {errors} failed. Emails sent.", 
            level=messages.SUCCESS if errors == 0 else messages.WARNING
        )
    
    process_selected.short_description = "Process selected completed deposits (with email)"
    
    def resend_status_emails(self, request, queryset):
        """Resend status emails for selected deposits"""
        sent, failed = resend_transaction_emails(queryset, 'deposit')
        self.message_user(
            request,
            f"Resent {sent} emails, {failed} failed.",
            level=messages.SUCCESS if failed == 0 else messages.WARNING
        )
    
    resend_status_emails.short_description = "Resend status emails"


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_usd', 'status', 'created_at', 'completed_at', 'email_sent_status']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id', 'user__email']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    actions = [
        'mark_as_completed', 'mark_as_failed', 'mark_as_processing',
        'process_selected', 'resend_status_emails'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'payment_method')
        }),
        ('Amount Details', {
            'fields': ('amount_usd', 'crypto_amount')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'wallet_address', 'network')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_name', 'account_number', 'routing_number', 'swift_code', 'iban')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'created_at', 'updated_at')
        }),
    )
    
    def email_sent_status(self, obj):
        """Display if email was sent"""
        return "✅" if hasattr(obj, 'email_sent') and obj.email_sent else "❌"
    email_sent_status.short_description = "Email"
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        errors = 0
        insufficient = 0
        
        for withdrawal in queryset:
            if withdrawal.status != 'completed':
                try:
                    with transaction.atomic():
                        withdrawal.status = 'completed'
                        withdrawal.save()
                        
                        # Process the withdrawal
                        success = process_completed_withdrawal(withdrawal)
                        if success:
                            updated += 1
                        else:
                            insufficient += 1
                            errors += 1
                except Exception as e:
                    errors += 1
                    self.message_user(
                        request, 
                        f"Error processing withdrawal {withdrawal.id}: {str(e)}", 
                        level=messages.ERROR
                    )
        
        if updated > 0:
            self.message_user(
                request, 
                f"{updated} withdrawals marked as completed and processed. Emails sent.", 
                level=messages.SUCCESS
            )
        if insufficient > 0:
            self.message_user(
                request, 
                f"{insufficient} withdrawals failed due to insufficient balance. Failure emails sent.", 
                level=messages.WARNING
            )
        if errors > 0:
            self.message_user(
                request, 
                f"{errors} withdrawals failed to process.", 
                level=messages.ERROR
            )
    
    mark_as_completed.short_description = "Mark selected as completed and process (with email)"
    
    def mark_as_failed(self, request, queryset):
        updated = 0
        for withdrawal in queryset:
            process_failed_withdrawal(withdrawal, "Marked as failed by admin")
            updated += 1
        
        self.message_user(
            request, 
            f"{updated} withdrawals marked as failed. Notification emails sent.", 
            level=messages.SUCCESS
        )
    
    mark_as_failed.short_description = "Mark selected as failed (with email)"
    
    def mark_as_processing(self, request, queryset):
        updated = 0
        for withdrawal in queryset:
            withdrawal.status = 'processing'
            withdrawal.save()
            
            # Send processing email
            from .email_utils import send_withdrawal_status_update_email
            try:
                send_withdrawal_status_update_email(withdrawal)
            except:
                pass
            
            updated += 1
        
        self.message_user(
            request, 
            f"{updated} withdrawals marked as processing. Status emails sent.", 
            level=messages.SUCCESS
        )
    
    mark_as_processing.short_description = "Mark selected as processing (with email)"
    
    def process_selected(self, request, queryset):
        """Process selected withdrawals without changing status"""
        processed = 0
        errors = 0
        insufficient = 0
        
        for withdrawal in queryset.filter(status='completed', completed_at__isnull=True):
            try:
                success = process_completed_withdrawal(withdrawal)
                if success:
                    processed += 1
                else:
                    insufficient += 1
                    errors += 1
            except Exception as e:
                errors += 1
        
        self.message_user(
            request, 
            f"{processed} withdrawals processed, {insufficient} insufficient balance, {errors} failed. Emails sent.", 
            level=messages.SUCCESS if errors == 0 else messages.WARNING
        )
    
    process_selected.short_description = "Process selected completed withdrawals (with email)"
    
    def resend_status_emails(self, request, queryset):
        """Resend status emails for selected withdrawals"""
        sent, failed = resend_transaction_emails(queryset, 'withdrawal')
        self.message_user(
            request,
            f"Resent {sent} emails, {failed} failed.",
            level=messages.SUCCESS if failed == 0 else messages.WARNING
        )
    
    resend_status_emails.short_description = "Resend status emails"


# Register your models here.
admin.site.register(User)
admin.site.register(PaymentMethod)
admin.site.register(PaymentMethodDetail)
admin.site.register(Deposit)
admin.site.register(Withdrawal)
admin.site.register(CopyTrade)
admin.site.register(LoyaltyStatus)
admin.site.register(Trader)
admin.site.register(Transaction)
admin.site.register(Referral)
admin.site.register(LoginHistory)
admin.site.register(Notification)