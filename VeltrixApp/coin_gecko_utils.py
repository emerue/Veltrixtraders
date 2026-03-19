# yourapp/coin_gecko_utils.py

import requests
from django.core.cache import cache
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# CoinGecko API configuration
COINGECKO_API_KEY = 'CG-k68RgDHSekjAzcGZufi7huD6'
COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'

# Mapping of our crypto symbols to CoinGecko IDs
CRYPTO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDT_ERC20': 'tether',
    'USDT_TRC20': 'tether',
    'SOL': 'solana',
    'XRP': 'ripple',
}

# Fiat currency codes for exchange rates
FIAT_CURRENCIES = ['USD', 'GBP', 'EUR', 'CZK', 'CNY', 'CAD', 'JPY']

def get_crypto_price(crypto_symbol, vs_currency='usd'):
    """
    Get real-time price for a cryptocurrency (price in USD)
    """
    cache_key = f'crypto_price_{crypto_symbol}_{vs_currency}'
    cached_price = cache.get(cache_key)
    
    if cached_price is not None:
        return Decimal(str(cached_price))
    
    try:
        coin_id = CRYPTO_IDS.get(crypto_symbol)
        if not coin_id:
            logger.error(f"Unknown crypto symbol: {crypto_symbol}")
            return None
        
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'x_cg_demo_api_key': COINGECKO_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if coin_id in data and vs_currency in data[coin_id]:
            price = Decimal(str(data[coin_id][vs_currency]))
            # Cache for 5 minutes
            cache.set(cache_key, float(price), 300)
            return price
        else:
            logger.error(f"Unexpected response format: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching crypto price: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_crypto_price: {e}")
        return None

def get_crypto_prices(crypto_symbols, vs_currency='usd'):
    """
    Get real-time prices for multiple cryptocurrencies (prices in USD)
    """
    cache_key = f'crypto_prices_{"_".join(crypto_symbols)}_{vs_currency}'
    cached_prices = cache.get(cache_key)
    
    if cached_prices is not None:
        return {k: Decimal(str(v)) for k, v in cached_prices.items()}
    
    try:
        coin_ids = []
        symbol_to_id = {}
        for symbol in crypto_symbols:
            coin_id = CRYPTO_IDS.get(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id[symbol] = coin_id
        
        if not coin_ids:
            return {}
        
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': vs_currency,
            'x_cg_demo_api_key': COINGECKO_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        prices = {}
        
        for symbol, coin_id in symbol_to_id.items():
            if coin_id in data and vs_currency in data[coin_id]:
                prices[symbol] = Decimal(str(data[coin_id][vs_currency]))
        
        cache.set(cache_key, {k: float(v) for k, v in prices.items()}, 300)
        return prices
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error in get_crypto_prices: {e}")
        return {}

def get_fiat_exchange_rates(base_currency='USD'):
    """
    Get real-time fiat exchange rates
    Returns rates in format: 1 USD = X Foreign Currency
    """
    cache_key = f'fiat_rates_{base_currency}'
    cached_rates = cache.get(cache_key)
    
    if cached_rates is not None:
        return cached_rates
    
    try:
        # Frankfurter API - free, no key required
        url = f"https://api.frankfurter.app/latest"
        params = {
            'from': base_currency,
            'to': ','.join([c for c in FIAT_CURRENCIES if c != 'USD'])
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rates = data.get('rates', {})
        
        # Add USD to USD rate
        rates['USD'] = 1.0
        
        # Cache for 1 hour
        cache.set(cache_key, rates, 3600)
        return rates
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching fiat rates: {e}")
        # Return fallback rates (1 USD = X Foreign Currency)
        fallback_rates = {
            'USD': 1.0,
            'GBP': 0.77,  # 1 USD = 0.77 GBP
            'EUR': 0.92,   # 1 USD = 0.92 EUR
            'CZK': 23.1,   # 1 USD = 23.1 CZK
            'CNY': 7.23,   # 1 USD = 7.23 CNY
            'CAD': 1.43,   # 1 USD = 1.43 CAD
            'JPY': 149.8,  # 1 USD = 149.8 JPY
        }
        return fallback_rates

def get_all_exchange_rates():
    """
    Get all exchange rates with USD as base
    Returns: {
        'USD': 1.0,
        'GBP': 0.77,  # 1 USD = 0.77 GBP
        'EUR': 0.92,  # 1 USD = 0.92 EUR
        'BTC': 65000, # 1 BTC = 65000 USD
        ...
    }
    """
    cache_key = 'all_exchange_rates_usd_base'
    cached_rates = cache.get(cache_key)
    
    if cached_rates is not None:
        return cached_rates
    
    # Get fiat rates (1 USD = X Foreign Currency)
    fiat_rates = get_fiat_exchange_rates()
    
    # Get crypto rates (price in USD: 1 Crypto = X USD)
    crypto_symbols = list(CRYPTO_IDS.keys())
    crypto_usd_prices = get_crypto_prices(crypto_symbols, 'usd')
    
    # Combine all rates
    all_rates = {}
    
    # Add fiat rates (1 USD = X Foreign Currency)
    for currency, rate in fiat_rates.items():
        all_rates[currency] = float(rate)
    
    # Add crypto rates (1 Crypto = X USD)
    for symbol, price in crypto_usd_prices.items():
        all_rates[symbol] = float(price)
    
    # Cache for 5 minutes
    cache.set(cache_key, all_rates, 300)
    
    return all_rates

def get_conversion_rate(from_currency, to_currency='USD'):
    """
    Get conversion rate from one currency to another
    Example: from_currency='GBP', to_currency='USD' returns how many USD per 1 GBP
    """
    rates = get_all_exchange_rates()
    
    if from_currency == to_currency:
        return 1.0
    
    if from_currency in rates and to_currency == 'USD':
        # If we have rate for from_currency (1 USD = X from_currency)
        # Then 1 from_currency = 1/rate USD
        return 1.0 / rates[from_currency]
    
    if from_currency == 'USD' and to_currency in rates:
        # 1 USD = rate to_currency
        return rates[to_currency]
    
    # For crypto to USD, rates already give price in USD
    if from_currency in rates and to_currency == 'USD':
        return rates[from_currency]
    
    return 1.0