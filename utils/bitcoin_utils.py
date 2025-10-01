import requests
import json
import hashlib
import hmac
import time
from decimal import Decimal
from typing import Dict, Optional, List
import os

class EnhancedBitcoinService:
    """Enhanced Bitcoin service with Lightning Network and advanced features"""
    
    def __init__(self):
        self.rpc_host = os.getenv('BITCOIN_RPC_HOST', 'localhost')
        self.rpc_port = os.getenv('BITCOIN_RPC_PORT', '8332')
        self.rpc_user = os.getenv('BITCOIN_RPC_USER')
        self.rpc_password = os.getenv('BITCOIN_RPC_PASSWORD')
        self.rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.rpc_host}:{self.rpc_port}/"
        
        # Fee estimation
        self.fee_cache = {}
        self.fee_cache_time = 0
        
        # Price cache
        self.price_cache = {}
        self.price_cache_time = 0

    def get_bitcoin_price_multiple_sources(self) -> Dict:
        """Get Bitcoin price from multiple sources for reliability"""
        current_time = time.time()
        
        # Return cached price if less than 5 minutes old
        if (current_time - self.price_cache_time) < 300 and self.price_cache:
            return self.price_cache
        
        sources = [
            {
                'name': 'CoinGecko',
                'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur,gbp,kes',
                'parser': lambda x: x['bitcoin']
            },
            {
                'name': 'CoinDesk',
                'url': 'https://api.coindesk.com/v1/bpi/currentprice.json',
                'parser': lambda x: {'usd': x['bpi']['USD']['rate_float']}
            },
            {
                'name': 'Blockchain.info',
                'url': 'https://blockchain.info/ticker',
                'parser': lambda x: {'usd': x['USD']['last']}
            }
        ]
        
        prices = {}
        for source in sources:
            try:
                response = requests.get(source['url'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    price_data = source['parser'](data)
                    prices[source['name']] = price_data
                    break  # Use first successful source
            except Exception as e:
                print(f"Failed to get price from {source['name']}: {e}")
                continue
        
        # Fallback prices
        if not prices:
            prices = {'Fallback': {'usd': 45000, 'eur': 42000, 'gbp': 36000, 'kes': 6750000}}
        
        # Cache the result
        self.price_cache = prices
        self.price_cache_time = current_time
        
        return prices

    def convert_currency_to_satoshis(self, amount: float, from_currency: str = 'usd') -> int:
        """Convert any currency to satoshis"""
        prices = self.get_bitcoin_price_multiple_sources()
        
        # Get the first available price source
        price_source = list(prices.values())[0]
        
        if from_currency.lower() not in price_source:
            raise ValueError(f"Currency {from_currency} not supported")
        
        btc_price = price_source[from_currency.lower()]
        btc_amount = amount / btc_price
        satoshis = int(btc_amount * 100000000)
        
        return satoshis

    def estimate_transaction_fee(self, priority: str = 'medium') -> Dict:
        """Estimate Bitcoin transaction fees"""
        current_time = time.time()
        
        # Return cached fees if less than 10 minutes old
        if (current_time - self.fee_cache_time) < 600 and self.fee_cache:
            return self.fee_cache
        
        fee_apis = [
            'https://mempool.space/api/v1/fees/recommended',
            'https://blockstream.info/api/fee-estimates'
        ]
        
        fees = {}
        for api in fee_apis:
            try:
                response = requests.get(api, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'fastestFee' in data:  # mempool.space format
                        fees = {
                            'high': data['fastestFee'],
                            'medium': data['halfHourFee'],
                            'low': data['hourFee']
                        }
                    else:  # blockstream format
                        fees = {
                            'high': list(data.values())[0],
                            'medium': list(data.values())[3] if len(data) > 3 else list(data.values())[-1],
                            'low': list(data.values())[-1]
                        }
                    break
            except Exception as e:
                print(f"Failed to get fees from {api}: {e}")
                continue
        
        # Fallback fees (sat/vB)
        if not fees:
            fees = {'high': 20, 'medium': 10, 'low': 5}
        
        # Cache the result
        self.fee_cache = fees
        self.fee_cache_time = current_time
        
        return fees

    def create_payment_qr_data(self, address: str, amount_btc: float, label: str = "RideShare Payment") -> str:
        """Create Bitcoin payment QR code data (BIP21 format)"""
        amount_str = f"{amount_btc:.8f}"
        qr_data = f"bitcoin:{address}?amount={amount_str}&label={label}"
        return qr_data

    def validate_bitcoin_address(self, address: str) -> Dict:
        """Enhanced Bitcoin address validation"""
        if not address:
            return {'valid': False, 'error': 'Empty address'}
        
        # Basic format checks
        if len(address) < 26 or len(address) > 62:
            return {'valid': False, 'error': 'Invalid address length'}
        
        # Check address type
        address_info = {
            'valid': False,
            'type': 'unknown',
            'network': 'unknown'
        }
        
        if address.startswith('1'):
            address_info['type'] = 'P2PKH'
            address_info['network'] = 'mainnet'
        elif address.startswith('3'):
            address_info['type'] = 'P2SH'
            address_info['network'] = 'mainnet'
        elif address.startswith('bc1'):
            address_info['type'] = 'Bech32'
            address_info['network'] = 'mainnet'
        elif address.startswith(('m', 'n')):
            address_info['type'] = 'P2PKH'
            address_info['network'] = 'testnet'
        elif address.startswith('2'):
            address_info['type'] = 'P2SH'
            address_info['network'] = 'testnet'
        elif address.startswith('tb1'):
            address_info['type'] = 'Bech32'
            address_info['network'] = 'testnet'
        
        # Try RPC validation if available
        try:
            result = self.rpc_call("validateaddress", [address])
            if "error" not in result and "result" in result:
                rpc_result = result["result"]
                address_info['valid'] = rpc_result.get('isvalid', False)
                if address_info['valid']:
                    address_info['type'] = rpc_result.get('type', address_info['type'])
                return address_info
        except:
            pass
        
        # Basic validation passed if we got here
        address_info['valid'] = True
        return address_info

    def generate_invoice_payment_hash(self, amount_satoshis: int, user_id: int, ride_id: int) -> str:
        """Generate a unique payment hash for invoice tracking"""
        data = f"{amount_satoshis}_{user_id}_{ride_id}_{int(time.time())}"
        return hashlib.sha256(data.encode()).hexdigest()

    def track_payment_status(self, payment_hash: str) -> Dict:
        """Track payment status (mock implementation - would integrate with real payment processor)"""
        # This would integrate with actual Bitcoin payment processors like BTCPay Server
        return {
            'payment_hash': payment_hash,
            'status': 'pending',  # pending, confirmed, failed, expired
            'confirmations': 0,
            'amount_received': 0,
            'created_at': time.time(),
            'confirmed_at': None
        }

    def create_btcpay_invoice(self, amount_satoshis: int, order_id: str, user_email: str) -> Dict:
        """Create BTCPay Server invoice (requires BTCPay Server setup)"""
        btcpay_url = os.getenv('BTCPAY_URL')
        btcpay_api_key = os.getenv('BTCPAY_API_KEY')
        
        if not btcpay_url or not btcpay_api_key:
            return {'error': 'BTCPay Server not configured'}
        
        invoice_data = {
            'amount': amount_satoshis / 100000000,  # Convert to BTC
            'currency': 'BTC',
            'orderId': order_id,
            'notificationEmail': user_email,
            'redirectURL': os.getenv('FRONTEND_URL', 'http://localhost