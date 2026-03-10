from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Trader, PaymentMethod

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms_accepted = forms.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'title', 'first_name', 'last_name', 'phone', 'date_of_birth',
            'house_no', 'address', 'city', 'province', 'zip_code', 'country',
            'email_deposit', 'email_withdrawal', 'email_trade', 'email_account_update',
            'push_deposit', 'push_withdrawal', 'push_trade'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class TwoFactorForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6)

class VerificationForm(forms.Form):
    DOCUMENT_CHOICES = [
        ('id', 'ID Card'),
        ('passport', 'Passport'),
        ('driver-license', "Driver's License"),
    ]
    
    document_type = forms.ChoiceField(choices=DOCUMENT_CHOICES, widget=forms.RadioSelect)
    document_number = forms.CharField(max_length=100)
    expiration_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    front_image = forms.ImageField()
    back_image = forms.ImageField()

class SetupPersonalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['title', 'first_name', 'last_name', 'date_of_birth']

class SetupContactForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['house_no', 'address', 'city', 'province', 'zip_code', 'country', 'phone']

class SetupExperienceForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['yrs_experience', 'trading_frequency', 'instrument_traded', 'knowledge_level', 'preferred_market', 'trading_platform']

class SetupEarningsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['annual_income', 'source_of_income', 'tax_residence']

class DepositForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[])
    amount = forms.DecimalField(min_value=1, max_digits=20, decimal_places=2)
    
    def __init__(self, *args, **kwargs):
        payment_choices = kwargs.pop('payment_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].choices = payment_choices

class DepositProofForm(forms.Form):
    proof_image = forms.ImageField(required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)


class WithdrawalForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    amount = forms.DecimalField(min_value=10, max_digits=20, decimal_places=2)
    
    # Crypto fields
    wallet_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter wallet address'}))
    network = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter network'}))
    
    # Bank fields
    bank_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter bank name'}))
    account_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter account name'}))
    account_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter account number'}))
    routing_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter routing number'}))
    swift_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter SWIFT code'}))
    iban = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter IBAN'}))
    
    def __init__(self, *args, **kwargs):
        payment_choices = kwargs.pop('payment_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].choices = payment_choices
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method_id = cleaned_data.get('payment_method')
        
        if payment_method_id:
            try:
                payment_method = PaymentMethod.objects.get(id=payment_method_id)
                
                # Validate based on method type
                if payment_method.method_type == 'crypto':
                    if not cleaned_data.get('wallet_address'):
                        self.add_error('wallet_address', 'Wallet address is required for crypto withdrawals')
                    if not cleaned_data.get('network'):
                        self.add_error('network', 'Network is required for crypto withdrawals')
                else:  # bank
                    if not cleaned_data.get('bank_name'):
                        self.add_error('bank_name', 'Bank name is required for bank withdrawals')
                    if not cleaned_data.get('account_name'):
                        self.add_error('account_name', 'Account name is required for bank withdrawals')
                    if not cleaned_data.get('account_number'):
                        self.add_error('account_number', 'Account number is required for bank withdrawals')
            except PaymentMethod.DoesNotExist:
                self.add_error('payment_method', 'Invalid payment method')
        
        return cleaned_data