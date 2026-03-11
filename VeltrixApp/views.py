from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import json
import os
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from django.utils.html import mark_safe

from .models import (
    User, Trader, CopyTrade, Transaction, Referral, LoginHistory, 
    Notification, PaymentMethod, PaymentMethodDetail, Deposit, Withdrawal, LoyaltyStatus
)
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileForm, ProfileImageForm,
    PasswordChangeForm, TwoFactorForm, VerificationForm, SetupPersonalForm,
    SetupContactForm, SetupExperienceForm, SetupEarningsForm, DepositForm,
    DepositProofForm, WithdrawalForm
)
from .email_utils import (
    send_welcome_email, send_deposit_confirmation_email, 
    send_withdrawal_confirmation_email, send_password_changed_email, send_password_reset_email
)
from django.urls import reverse
from .models import User, PasswordResetToken
from .forms import ForgotPasswordForm, ResetPasswordForm, PasswordChangeForm


# Helper function to load traders from JSON
def load_traders_from_json():
    traders = []
    json_file_path = os.path.join(settings.BASE_DIR, 'traders.json')
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            traders_data = data.get('traders', [])
            
            for trader_data in traders_data:
                Trader.objects.update_or_create(
                    id=trader_data['id'],
                    defaults={
                        'name': trader_data['name'],
                        'image_url': trader_data['image_url'],
                        'risk_level': trader_data['risk_level'],
                        'specialty': trader_data['specialty'],
                        'monthly_return': trader_data['monthly_return'],
                        'yearly_return': trader_data['yearly_return'],
                        'win_rate': trader_data['win_rate'],
                        'experience_years': trader_data['experience_years'],
                        'description': trader_data.get('description', ''),
                        'fee_percentage': trader_data['fee_percentage'],
                        'min_investment': trader_data['min_investment'],
                        'followers': trader_data['followers'],
                    }
                )
            traders = Trader.objects.all()
    except FileNotFoundError:
        print("traders.json not found")
    except json.JSONDecodeError:
        print("Invalid JSON in traders.json")
    
    return traders

# Public Views
def home(request):
    return render(request, 'home.html')

def construction(request):
    return render(request, 'construction.html')

def about(request):
    return render(request, 'about.html')

def software(request):
    return render(request, 'software.html')

def insight(request):
    return render(request, 'insight.html')

def copy_trading_public(request):
    return render(request, 'option-copy-trading.html')

def advance_trading(request):
    return render(request, 'advance-trading.html')

def live_trading(request):
    return render(request, 'live-trading.html')

def swing_trading(request):
    return render(request, 'swing-trading.html')

def feature_trading(request):
    return render(request, 'futures.html')

def options_trading(request):
    return render(request, 'option-trading.html')

def oil_and_gas(request):
    return render(request, 'oil-and-gas.html')

def terms_and_conditions(request):
    return render(request, 'terms-and-conditions.html')

def privacy_policy(request):
    return render(request, 'privacy-policy.html')

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            
            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                print(f"Error sending welcome email: {e}")
            
            # Check if referred
            ref_code = request.GET.get('ref')
            if ref_code:
                try:
                    referrer = User.objects.get(referral_code=ref_code)
                    Referral.objects.create(referrer=referrer, referred_user=user)
                except User.DoesNotExist:
                    pass
            
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('setup_personal')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = None

            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                LoginHistory.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )

                return redirect('dashboard')

            messages.error(request, "Invalid email/username or password")

    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')

# Setup Views
@login_required
def setup_personal(request):
    if request.method == 'POST':
        form = SetupPersonalForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal information saved!')
            return redirect('setup_contact')
    else:
        form = SetupPersonalForm(instance=request.user)
    
    return render(request, 'setup-user-info.html', {'form': form})

@login_required
def setup_contact(request):
    if request.method == 'POST':
        form = SetupContactForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact information saved!')
            return redirect('setup_experience')
    else:
        form = SetupContactForm(instance=request.user)
    
    return render(request, 'setup-contact.html', {'form': form})

@login_required
def setup_experience(request):
    if request.method == 'POST':
        form = SetupExperienceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trading experience saved!')
            return redirect('setup_earnings')
    else:
        form = SetupExperienceForm(instance=request.user)
    
    return render(request, 'setup-experience.html', {'form': form})

@login_required
def setup_earnings(request):
    if request.method == 'POST':
        form = SetupEarningsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Earnings information saved!')
            return redirect('setup_declaration')
    else:
        form = SetupEarningsForm(instance=request.user)
    
    return render(request, 'setup-earnings.html', {'form': form})

@login_required
def setup_declaration(request):
    if request.method == 'POST':
        # Mark profile as complete
        request.user.save()
        messages.success(request, 'Profile completed successfully!')
        return redirect('dashboard')
    
    return render(request, 'setup-declaration.html')

# Dashboard Views
@login_required
def dashboard(request):
    traders = Trader.objects.filter(is_active=True)[:10]
    
    context = {
        'traders': traders,
        'user': request.user,
    }
    return render(request, 'user/dashboard.html', context)

@login_required
def copy_trading(request):
    if request.method == 'POST':
        trader_id = request.POST.get('trader_id')
        amount = request.POST.get('amount')
        action = request.POST.get('action', 'start')  # 'start' or 'stop'
        
        if action == 'stop':
            # Handle stop copy trade
            trade_id = request.POST.get('trade_id')
            copy_trade = get_object_or_404(CopyTrade, id=trade_id, user=request.user, status='active')
            
            copy_trade.status = 'stopped'
            copy_trade.save()
            
            # Create transaction record for stopping (optional - you can remove this if no refund)
            Transaction.objects.create(
                user=request.user,
                transaction_type='trade',
                amount=copy_trade.amount,
                status='completed',
                reference_id=f"STOP-{copy_trade.id}",
                description=f'Stopped copy trade with {copy_trade.trader.name}'
            )
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title='Copy Trade Stopped',
                message=f'You have stopped copying {copy_trade.trader.name}.'
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Stopped copying {copy_trade.trader.name}',
                    'type': 'success',
                    'trade_id': copy_trade.id
                })
            
            messages.success(request, f'Stopped copying {copy_trade.trader.name}')
            return redirect('copy_trading')
        
        else:
            # Handle start copy trade (existing code)
            trader = get_object_or_404(Trader, id=trader_id)
            
            # Check if amount is provided
            if not amount:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Amount is required',
                        'type': 'error'
                    })
                messages.error(request, 'Amount is required')
                return redirect('copy_trading')
            
            try:
                amount = Decimal(amount)
            except:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid amount format',
                        'type': 'error'
                    })
                messages.error(request, 'Invalid amount format')
                return redirect('copy_trading')
            
            # Check minimum investment
            if amount < trader.min_investment:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Minimum investment is ${trader.min_investment}',
                        'type': 'error',
                        'min_investment': float(trader.min_investment)
                    })
                messages.error(request, f'Minimum investment for {trader.name} is ${trader.min_investment}')
                return redirect('copy_trading')
            
            # Check if already copying
            existing = CopyTrade.objects.filter(
                user=request.user, 
                trader=trader, 
                status='active'
            ).first()
            
            if existing:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'You are already copying {trader.name}',
                        'type': 'warning'
                    })
                messages.warning(request, f'You are already copying {trader.name}')
                return redirect('copy_trading')
            
            # Check balance
            if request.user.balance < amount:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Insufficient balance. You need ${amount - request.user.balance} more.',
                        'type': 'error',
                        'balance': float(request.user.balance),
                        'required': float(amount)
                    })
                messages.error(
                    request, 
                    f'Insufficient balance. You need ${amount - request.user.balance:,.2f} more.'
                )
                return redirect('copy_trading')
            
            # Deduct balance and create copy trade
            user = request.user
            user.balance -= amount
            user.save()
            
            copy_trade = CopyTrade.objects.create(
                user=user,
                trader=trader,
                amount=amount,
                status='active'
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=user,
                transaction_type='trade',
                amount=amount,
                status='completed',
                reference_id=f"COPY-{copy_trade.id}",
                description=f'Copy trading investment in {trader.name}'
            )
            
            # Create notification
            Notification.objects.create(
                user=user,
                title='Copy Trade Started',
                message=f'You have started copying {trader.name} with ${amount:,.2f}'
            )
            
            # Update trader followers count
            trader.followers += 1
            trader.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Now copying {trader.name} with ${amount:,.2f}',
                    'type': 'success',
                    'new_balance': float(user.balance),
                    'copy_trade': {
                        'id': copy_trade.id,
                        'trader': trader.name,
                        'amount': float(amount),
                        'started_at': copy_trade.started_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': copy_trade.status
                    }
                })
            
            messages.success(request, f'Now copying {trader.name} with ${amount:,.2f}')
            return redirect('copy_trading')
    
    # GET request
    traders = Trader.objects.filter(is_active=True)[:15]
    active_copy_trades = CopyTrade.objects.filter(
        user=request.user, 
        status='active'
    ).select_related('trader')
    
    context = {
        'traders': traders,
        'active_copy_trades': active_copy_trades,
        'copy_trades_count': active_copy_trades.count(),
        'user': request.user,
    }
    return render(request, 'user/copytrading.html', context)

@login_required
def stop_copy_trade(request, trade_id):
    if request.method == 'POST':
        copy_trade = get_object_or_404(
            CopyTrade, 
            id=trade_id, 
            user=request.user,
            status='active'
        )
        
        # Refund the amount (optional - you might want to implement a different logic)
        user = request.user
        user.balance += copy_trade.amount
        user.save()
        
        copy_trade.status = 'stopped'
        copy_trade.save()
        
        # Create transaction for refund
        Transaction.objects.create(
            user=user,
            transaction_type='trade',
            amount=copy_trade.amount,
            status='completed',
            reference_id=f"REFUND-{copy_trade.id}",
            description=f'Refund from stopping copy trade with {copy_trade.trader.name}'
        )
        
        # Create notification
        Notification.objects.create(
            user=user,
            title='Copy Trade Stopped',
            message=f'You have stopped copying {copy_trade.trader.name}. ${copy_trade.amount:,.2f} has been refunded.'
        )
        
        messages.success(
            request, 
            f'Stopped copying {copy_trade.trader.name}. ${copy_trade.amount:,.2f} refunded.'
        )
    
    return redirect('copy_trading')

from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def copy_traders(request):
    # Get all active traders
    traders = Trader.objects.filter(is_active=True)
    
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'monthly_return')
    sort_direction = request.GET.get('direction', 'desc')
    risk_levels = request.GET.getlist('risk')
    specialties = request.GET.getlist('specialty')
    status = request.GET.getlist('status', ['active'])
    min_monthly = request.GET.get('min_monthly', 0)
    max_fee = request.GET.get('max_fee', 100)
    
    # Apply search filter
    if search_query:
        traders = traders.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(specialty__icontains=search_query)
        )
    
    # Apply risk level filter
    if risk_levels:
        traders = traders.filter(risk_level__in=risk_levels)
    
    # Apply specialty filter
    if specialties:
        traders = traders.filter(specialty__in=specialties)
    
    # Apply status filter
    if 'active' in status:
        traders = traders.filter(is_active=True)
    
    # Apply minimum monthly return filter
    if min_monthly:
        try:
            min_monthly = float(min_monthly)
            traders = traders.filter(monthly_return__gte=min_monthly)
        except ValueError:
            pass
    
    # Apply maximum fee filter
    if max_fee:
        try:
            max_fee = float(max_fee)
            traders = traders.filter(fee_percentage__lte=max_fee)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_direction == 'desc':
        sort_field = f'-{sort_by}'
    else:
        sort_field = sort_by
    
    traders = traders.order_by(sort_field)
    
    # Pagination
    paginator = Paginator(traders, 12)  # Show 12 traders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'traders': page_obj,
        'total_traders': traders.count(),
        'current_filters': {
            'search': search_query,
            'sort': sort_by,
            'direction': sort_direction,
            'risk': risk_levels,
            'specialty': specialties,
            'status': status,
            'min_monthly': min_monthly,
            'max_fee': max_fee,
        }
    }
    return render(request, 'user/copytraders.html', context)

@login_required
def deposit(request):
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Prepare payment methods for JSON
    payment_methods_json = []
    for pm in payment_methods:
        payment_methods_json.append({
            'id': pm.id,
            'name': pm.name,
            'method_type': pm.method_type,
            'crypto_symbol': pm.crypto_symbol,
            'instructions': pm.instructions,
            'processing_time': pm.processing_time,
            'withdrawal_fee': float(pm.withdrawal_fee),
        })
    
    # Mock exchange rates
    exchange_rates = {
        'BTC': 0.000014,
        'ETH': 0.0005,
        'USDT': 1.0,
        'SOL': 0.012,
        'XRP': 0.73,
    }
    
    if request.method == 'POST':
        form = DepositForm(request.POST, payment_choices=[(pm.id, pm.name) for pm in payment_methods])
        if form.is_valid():
            payment_method_id = form.cleaned_data['payment_method']
            amount = form.cleaned_data['amount']
            
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
            
            # Create deposit record
            deposit = Deposit.objects.create(
                user=request.user,
                payment_method=payment_method,
                amount_usd=amount,
                status='pending'
            )
            
            # Calculate crypto amount if applicable
            if payment_method.method_type == 'crypto' and payment_method.crypto_symbol in exchange_rates:
                deposit.crypto_amount = amount * Decimal(str(exchange_rates[payment_method.crypto_symbol]))
                deposit.save()
            
            # Send confirmation email
            try:
                send_deposit_confirmation_email(deposit)
            except Exception as e:
                print(f"Error sending deposit email: {e}")
            
            # Redirect to confirmation page
            return redirect('deposit_confirmation', deposit_id=deposit.id)
    else:
        form = DepositForm(payment_choices=[(pm.id, pm.name) for pm in payment_methods])
    
    context = {
        'form': form,
        'payment_methods': payment_methods,
        'payment_methods_json': json.dumps(payment_methods_json),
        'exchange_rates_json': json.dumps(exchange_rates),
    }
    return render(request, 'user/deposit.html', context)

@login_required
def deposit_confirmation(request, deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id, user=request.user)
    
    # Get payment method details
    payment_details = PaymentMethodDetail.objects.filter(
        payment_method=deposit.payment_method, 
        is_default=True
    ).first()
    
    if not payment_details:
        payment_details = PaymentMethodDetail.objects.filter(
            payment_method=deposit.payment_method
        ).first()
    
    context = {
        'deposit': deposit,
        'payment_details': payment_details,
    }
    return render(request, 'user/deposit-confirmation.html', context)

@login_required
def upload_deposit_proof(request, deposit_id):
    deposit = get_object_or_404(Deposit, id=deposit_id, user=request.user)
    
    if request.method == 'POST':
        form = DepositProofForm(request.POST, request.FILES)
        if form.is_valid():
            deposit.proof_image = form.cleaned_data['proof_image']
            deposit.notes = form.cleaned_data['notes']
            deposit.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title='Deposit Proof Submitted',
                message=f'Your deposit proof for ${deposit.amount_usd} has been submitted and is under review.'
            )
            
            messages.success(request, 'Proof of payment uploaded successfully. Your deposit is now under review.')
            return redirect('deposit_confirmation', deposit_id=deposit.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('deposit_confirmation', deposit_id=deposit.id)


@login_required
def withdrawal(request):
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Prepare payment methods for JSON with proper Decimal handling
    payment_methods_json = []
    for pm in payment_methods:
        payment_methods_json.append({
            'id': pm.id,
            'name': pm.name,
            'method_type': pm.method_type,
            'crypto_symbol': pm.crypto_symbol,
            'processing_time': pm.processing_time,
            'withdrawal_fee': float(pm.withdrawal_fee),
        })
    
    # Mock exchange rates
    exchange_rates = {
        'BTC': 0.000014,
        'ETH': 0.0005,
        'USDT': 1.0,
        'SOL': 0.012,
        'XRP': 0.73,
    }
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, payment_choices=[(pm.id, pm.name) for pm in payment_methods])
        if form.is_valid():
            payment_method_id = form.cleaned_data['payment_method']
            amount = form.cleaned_data['amount']
            
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
            
            # Check balance
            if request.user.balance < amount:
                messages.error(request, 'Insufficient balance')
                return redirect('withdrawal')
            
            # Create withdrawal record
            withdrawal = Withdrawal.objects.create(
                user=request.user,
                payment_method=payment_method,
                amount_usd=amount,
                status='pending'
            )
            
            # Set withdrawal details based on method type
            if payment_method.method_type == 'crypto':
                withdrawal.wallet_address = form.cleaned_data.get('wallet_address', '')
                withdrawal.network = form.cleaned_data.get('network', '')
                
                # Calculate crypto amount
                crypto_symbol = payment_method.crypto_symbol
                # Handle USDT which might have different variants
                if crypto_symbol and crypto_symbol.startswith('USDT'):
                    crypto_key = 'USDT'
                else:
                    crypto_key = crypto_symbol
                    
                if crypto_key in exchange_rates:
                    rate = Decimal(str(exchange_rates[crypto_key]))
                    withdrawal.crypto_amount = amount * rate
            else:  # bank
                withdrawal.bank_name = form.cleaned_data.get('bank_name', '')
                withdrawal.account_name = form.cleaned_data.get('account_name', '')
                withdrawal.account_number = form.cleaned_data.get('account_number', '')
                withdrawal.routing_number = form.cleaned_data.get('routing_number', '')
                withdrawal.swift_code = form.cleaned_data.get('swift_code', '')
                withdrawal.iban = form.cleaned_data.get('iban', '')
            
            withdrawal.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='withdrawal',
                amount=amount,
                status='pending',
                reference_id=withdrawal.transaction_id,
                description=f'Withdrawal of ${amount} via {payment_method.name}'
            )
            
            # Send confirmation email
            try:
                send_withdrawal_confirmation_email(withdrawal)
            except Exception as e:
                print(f"Error sending withdrawal email: {e}")
            
            messages.success(request, 'Withdrawal request submitted successfully')
            return redirect('transactions')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WithdrawalForm(payment_choices=[(pm.id, pm.name) for pm in payment_methods])
    
    # Convert to JSON strings
    payment_methods_json_str = json.dumps(payment_methods_json)
    exchange_rates_json_str = json.dumps(exchange_rates)
    
    context = {
        'form': form,
        'payment_methods': payment_methods,
        'payment_methods_json': mark_safe(payment_methods_json_str),
        'exchange_rates_json': mark_safe(exchange_rates_json_str),
        'user': request.user,
    }
    return render(request, 'user/withdrawal.html', context)

@login_required
def technical_insights(request):
    return render(request, 'user/technical-insights.html')

@login_required
def economic_calendar(request):
    return render(request, 'user/economic-calendar.html')

@login_required
def loyalty_status(request):
    user = request.user
    
    # Get all active loyalty tiers
    loyalty_levels = LoyaltyStatus.objects.filter(is_active=True).order_by('level')
    
    # Get current user's tier
    current_tier = loyalty_levels.filter(name=user.loyalty_status).first()
    if not current_tier:
        current_tier = loyalty_levels.first()  # Default to lowest tier
    
    # Calculate next tier
    next_tier = loyalty_levels.filter(level__gt=current_tier.level).first()
    
    # Calculate progress to next tier
    total_deposits = user.total_deposit or 0
    
    if next_tier:
        next_level_needed = next_tier.min_deposit - total_deposits
        if next_level_needed < 0:
            next_level_needed = 0
        
        # Calculate progress percentage
        tier_range = next_tier.min_deposit - current_tier.min_deposit
        if tier_range > 0:
            progress = ((total_deposits - current_tier.min_deposit) / tier_range) * 100
        else:
            progress = 100
        progress = min(100, max(0, progress))
    else:
        next_level_needed = 0
        next_tier = current_tier
        progress = 100
    
    # Calculate max bonus percentages for UI
    max_bonus_percentage = loyalty_levels.last().bonus_percentage if loyalty_levels.exists() else 0
    max_referral_bonus = loyalty_levels.last().referral_bonus if loyalty_levels.exists() else 0
    
    # Prepare loyalty levels data for template
    levels_data = []
    for tier in loyalty_levels:
        level_data = {
            'name': tier.name,
            'level': tier.level,
            'icon': tier.icon,
            'min_deposit': tier.min_deposit,
            'direct_referral': tier.direct_referral_required,
            'referral_deposits': tier.referral_deposits_required,
            'bonus': tier.referral_bonus,
            'color': tier.color,
        }
        levels_data.append(level_data)
    
    context = {
        'current_level': {
            'name': current_tier.name,
            'level': current_tier.level,
            'icon': current_tier.icon,
            'color': current_tier.color,
        },
        'next_level': {
            'name': next_tier.name if next_tier else current_tier.name,
            'level': next_tier.level if next_tier else current_tier.level,
            'min_deposit': next_tier.min_deposit if next_tier else current_tier.min_deposit,
        },
        'loyalty_levels': levels_data,
        'total_deposits': total_deposits,
        'next_level_needed': next_level_needed,
        'next_level_progress': progress,
        'max_bonus_percentage': max_bonus_percentage,
        'max_referral_bonus': max_referral_bonus,
    }
    
    return render(request, 'user/loyalty-status.html', context)

@login_required
def transactions(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'transactions': user_transactions,
    }
    print(f"User {request.user.username} has {user_transactions.count()} transactions")
    return render(request, 'user/transactions.html', context)

@login_required
def verification(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.document_type = form.cleaned_data['document_type']
            user.document_number = form.cleaned_data['document_number']
            user.document_expiry = form.cleaned_data.get('expiration_date')
            user.document_front = form.cleaned_data['front_image']
            user.document_back = form.cleaned_data['back_image']
            user.save()
            
            messages.success(request, 'Verification documents submitted for review')
            return redirect('profile')
    else:
        form = VerificationForm()
    
    return render(request, 'user/verification.html', {'form': form})

@login_required
def login_history(request):
    history = LoginHistory.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'login_history': history,
    }
    return render(request, 'user/login-history.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'user/profile.html', context)

@login_required
def referral(request):
    referrals = Referral.objects.filter(referrer=request.user).select_related('referred_user')
    
    total_referrals = referrals.count()
    active_referrals = referrals.filter(referred_user__is_kyc_verified=True).count()
    total_commission = sum(r.commission_earned for r in referrals)
    
    context = {
        'referrals': [{
            'username': r.referred_user.username,
            'created_at': r.created_at,
            'status': 'active' if r.referred_user.is_kyc_verified else 'pending',
            'commission': r.commission_earned,
        } for r in referrals],
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'total_commission': total_commission,
        'user': request.user,
    }
    return render(request, 'user/referral.html', context)


def forgot_password(request):
    """Handle forgot password request - for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Invalidate any existing unused tokens
                PasswordResetToken.objects.filter(
                    user=user, used=False, expires_at__gt=timezone.now()
                ).update(used=True)
                
                # Create new token
                token = PasswordResetToken.objects.create(user=user)
                
                # Generate reset URL
                reset_url = request.build_absolute_uri(
                    reverse('reset_password', kwargs={'token': token.token})
                )
                
                # Send email
                try:
                    send_password_reset_email(user, reset_url)
                    messages.success(
                        request, 
                        'If an account exists with this email, you will receive password reset instructions.'
                    )
                except Exception as e:
                    # Log error but don't reveal to user
                    print(f"Email sending failed: {e}")
                    messages.success(
                        request,
                        'If an account exists with this email, you will receive password reset instructions.'
                    )
                    
            except User.DoesNotExist:
                # Don't reveal that user doesn't exist
                messages.success(
                    request,
                    'If an account exists with this email, you will receive password reset instructions.'
                )
            
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'forgot-password.html', {'form': form})

def reset_password(request, token):
    """Handle password reset with token"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get and validate token
    try:
        reset_token = PasswordResetToken.objects.get(token=token, used=False)
        if not reset_token.is_valid():
            messages.error(request, 'This password reset link has expired.')
            return redirect('forgot_password')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            # Send confirmation email
            try:
                send_password_changed_email(user)
            except Exception as e:
                print(f"Password changed email failed: {e}")
            
            messages.success(request, 'Your password has been reset successfully. You can now login.')
            return redirect('login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'reset-password.html', {
        'form': form,
        'valid_token': True,
        'email': reset_token.user.email
    })

@login_required
def password(request):
    """Handle password change for logged in users"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            # Verify current password
            if not request.user.check_password(form.cleaned_data['current_password']):
                messages.error(request, 'Current password is incorrect')
            else:
                # Update password
                request.user.set_password(form.cleaned_data['new_password'])
                request.user.save()
                
                # Send confirmation email
                try:
                    send_password_changed_email(request.user)
                except Exception as e:
                    print(f"Password changed email failed: {e}")
                
                messages.success(request, 'Password changed successfully')
                return redirect('profile')
    else:
        form = PasswordChangeForm()
    
    return render(request, 'user/password.html', {'form': form})

@login_required
def two_factor(request):
    if request.method == 'POST':
        if 'enable' in request.POST:
            # Generate secret
            secret = pyotp.random_base32()
            request.user.two_factor_secret = secret
            request.user.save()
            
            # Generate QR code
            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(request.user.email, issuer_name="Veltrixtraders")
            
            img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
            buffer = BytesIO()
            img.save(buffer)
            qr_code = base64.b64encode(buffer.getvalue()).decode()
            
            return render(request, 'user/two-factor.html', {'qr_code': qr_code, 'secret': secret})
        
        elif 'verify' in request.POST:
            form = TwoFactorForm(request.POST)
            if form.is_valid():
                totp = pyotp.TOTP(request.user.two_factor_secret)
                if totp.verify(form.cleaned_data['otp']):
                    request.user.two_factor_enabled = True
                    request.user.save()
                    messages.success(request, 'Two-factor authentication enabled')
                    return redirect('two_factor')
                else:
                    messages.error(request, 'Invalid OTP')
    
    return render(request, 'user/two-factor.html')

@login_required
def two_factor_verify(request):
    if request.method == 'POST':
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            totp = pyotp.TOTP(request.user.two_factor_secret)
            if totp.verify(form.cleaned_data['otp']):
                request.session.pop('2fa_required', None)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid OTP')
    else:
        form = TwoFactorForm()
    
    return render(request, 'user/two-factor-verify.html', {'form': form})

@login_required
def copy_trading_history(request):
    copy_trades = CopyTrade.objects.filter(user=request.user).select_related('trader')
    context = {
        'copy_trades': copy_trades,
    }
    return render(request, 'user/copytrading-history.html', context)

@login_required
def demo_history(request):
    return render(request, 'user/demo-history.html')

@login_required
def demo(request):
    return render(request, 'user/demo.html')

# Management Command to load traders
def load_traders(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    load_traders_from_json()
    messages.success(request, 'Traders loaded successfully')
    return redirect('dashboard')