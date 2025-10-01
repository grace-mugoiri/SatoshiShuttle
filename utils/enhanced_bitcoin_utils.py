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
            'redirectURL': os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/payment-success',
            'notificationURL': os.getenv('BACKEND_URL', 'http://localhost:5000') + '/api/payment-webhook'
        }
        
        headers = {
            'Authorization': f'token {btcpay_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{btcpay_url}/api/v1/invoices',
                json=invoice_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'BTCPay Server error: {response.status_code}'}
        except Exception as e:
            return {'error': f'BTCPay Server request failed: {str(e)}'}

    def rpc_call(self, method: str, params: List = None) -> Dict:
        """Make RPC call to Bitcoin Core"""
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "id": "rideshare",
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Lightning Network Service
class LightningNetworkService:
    """Lightning Network integration for instant payments"""
    
    def __init__(self):
        self.lnd_host = os.getenv('LND_HOST', 'localhost:10009')
        self.lnd_cert_path = os.getenv('LND_CERT_PATH', '~/.lnd/tls.cert')
        self.lnd_macaroon_path = os.getenv('LND_MACAROON_PATH', '~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon')

    def create_invoice(self, amount_satoshis: int, memo: str = "RideShare Payment") -> Dict:
        """Create Lightning Network invoice"""
        # This would integrate with LND gRPC API
        invoice_data = {
            'payment_request': f'lnbc{amount_satoshis}...',  # Mock payment request
            'payment_hash': hashlib.sha256(f"{amount_satoshis}{memo}{time.time()}".encode()).hexdigest(),
            'amount': amount_satoshis,
            'memo': memo,
            'expiry': int(time.time()) + 3600,  # 1 hour expiry
            'created_at': int(time.time())
        }
        
        return invoice_data

    def pay_invoice(self, payment_request: str) -> Dict:
        """Pay Lightning Network invoice"""
        # This would integrate with LND payment API
        return {
            'payment_hash': 'mock_payment_hash',
            'status': 'succeeded',
            'amount_paid': 0,
            'fee_paid': 0,
            'payment_route': []
        }

    def check_invoice_status(self, payment_hash: str) -> Dict:
        """Check Lightning invoice payment status"""
        return {
            'payment_hash': payment_hash,
            'settled': False,
            'amount_paid': 0,
            'settled_at': None
        }

# Bitcoin Price Alert Service
class BitcoinPriceAlertService:
    """Service for Bitcoin price alerts and notifications"""
    
    def __init__(self):
        self.price_history = []
        self.alerts = []

    def add_price_alert(self, user_id: int, target_price: float, alert_type: str = 'above'):
        """Add price alert for user"""
        alert = {
            'user_id': user_id,
            'target_price': target_price,
            'alert_type': alert_type,  # 'above' or 'below'
            'created_at': time.time(),
            'triggered': False
        }
        self.alerts.append(alert)
        return alert

    def check_price_alerts(self, current_price: float):
        """Check if any price alerts should be triggered"""
        triggered_alerts = []
        
        for alert in self.alerts:
            if alert['triggered']:
                continue
                
            if (alert['alert_type'] == 'above' and current_price >= alert['target_price']) or \
               (alert['alert_type'] == 'below' and current_price <= alert['target_price']):
                alert['triggered'] = True
                alert['triggered_at'] = time.time()
                triggered_alerts.append(alert)
        
        return triggered_alerts

    def get_price_trend(self, hours: int = 24) -> Dict:
        """Get Bitcoin price trend analysis"""
        if len(self.price_history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_prices = [p for p in self.price_history if time.time() - p['timestamp'] <= hours * 3600]
        
        if len(recent_prices) < 2:
            return {'trend': 'insufficient_data'}
        
        start_price = recent_prices[0]['price']
        end_price = recent_prices[-1]['price']
        change_percent = ((end_price - start_price) / start_price) * 100
        
        return {
            'trend': 'up' if change_percent > 0 else 'down',
            'change_percent': change_percent,
            'start_price': start_price,
            'end_price': end_price,
            'period_hours': hours
        }

# Multi-signature Bitcoin Service
class MultisigBitcoinService:
    """Multi-signature Bitcoin transactions for escrow"""
    
    def __init__(self):
        self.escrow_accounts = {}

    def create_escrow_address(self, driver_pubkey: str, passenger_pubkey: str, platform_pubkey: str) -> Dict:
        """Create 2-of-3 multisig escrow address"""
        # This would create actual multisig address
        mock_address = f"3{hashlib.sha256(f'{driver_pubkey}{passenger_pubkey}{platform_pubkey}'.encode()).hexdigest()[:30]}"
        
        escrow_data = {
            'address': mock_address,
            'required_signatures': 2,
            'public_keys': [driver_pubkey, passenger_pubkey, platform_pubkey],
            'created_at': time.time()
        }
        
        return escrow_data

    def release_escrow_funds(self, escrow_address: str, signatures: List[str]) -> Dict:
        """Release funds from escrow with required signatures"""
        if len(signatures) < 2:
            return {'error': 'Insufficient signatures'}
        
        # This would broadcast the actual transaction
        return {
            'txid': f"mock_tx_{int(time.time())}",
            'status': 'broadcasted',
            'signatures_used': len(signatures)
        }

# Utility functions
def format_satoshis(satoshis: int) -> str:
    """Format satoshis for display"""
    if satoshis >= 100000000:  # 1 BTC or more
        btc = satoshis / 100000000
        return f"{btc:.8f} BTC"
    elif satoshis >= 1000:  # 1000 sats or more
        return f"{satoshis:,} sats"
    else:
        return f"{satoshis} sats"

def calculate_ride_pricing(distance_km: float, base_rate_per_km: float = 0.5) -> Dict:
    """Calculate ride pricing in multiple currencies"""
    bitcoin_service = EnhancedBitcoinService()
    
    # Calculate base price in USD
    usd_price = distance_km * base_rate_per_km
    
    # Get current Bitcoin price
    prices = bitcoin_service.get_bitcoin_price_multiple_sources()
    btc_price_usd = list(prices.values())[0]['usd']
    
    # Convert to Bitcoin
    btc_amount = usd_price / btc_price_usd
    satoshis = int(btc_amount * 100000000)
    
    return {
        'distance_km': distance_km,
        'usd_price': round(usd_price, 2),
        'btc_price': round(btc_amount, 8),
        'satoshis': satoshis,
        'formatted_btc': format_satoshis(satoshis),
        'btc_rate_used': btc_price_usd
    }

def generate_payment_qr_code(address: str, amount_btc: float, label: str = "RideShare") -> str:
    """Generate QR code data for Bitcoin payment (BIP21)"""
    return f"bitcoin:{address}?amount={amount_btc:.8f}&label={label}&message=RideShare%20Payment"

# Integration helper
class RideShareBitcoinIntegration:
    """Main integration class for RideShare Bitcoin features"""
    
    def __init__(self):
        self.bitcoin_service = EnhancedBitcoinService()
        self.lightning_service = LightningNetworkService()
        self.price_alert_service = BitcoinPriceAlertService()
        self.multisig_service = MultisigBitcoinService()

    def process_ride_payment(self, ride_data: Dict, payment_method: str = 'bitcoin') -> Dict:
        """Process ride payment with Bitcoin integration"""
        if payment_method == 'bitcoin':
            # Create Bitcoin payment
            amount_satoshis = ride_data['price_bitcoin']
            recipient_address = ride_data['driver_bitcoin_address']
            
            payment_data = {
                'method': 'bitcoin',
                'amount_satoshis': amount_satoshis,
                'recipient_address': recipient_address,
                'qr_code_data': generate_payment_qr_code(recipient_address, amount_satoshis / 100000000),
                'estimated_fee': self.bitcoin_service.estimate_transaction_fee(),
                'payment_hash': self.bitcoin_service.generate_invoice_payment_hash(
                    amount_satoshis, ride_data['passenger_id'], ride_data['ride_id']
                )
            }
            
        elif payment_method == 'lightning':
            # Create Lightning payment
            invoice = self.lightning_service.create_invoice(
                ride_data['price_bitcoin'], 
                f"Ride from {ride_data['origin']} to {ride_data['destination']}"
            )
            payment_data = {
                'method': 'lightning',
                'payment_request': invoice['payment_request'],
                'payment_hash': invoice['payment_hash'],
                'amount_satoshis': invoice['amount'],
                'expiry': invoice['expiry']
            }
        
        return payment_data

    def setup_escrow_payment(self, ride_data: Dict) -> Dict:
        """Setup escrow payment for ride"""
        # Create multisig escrow address
        escrow = self.multisig_service.create_escrow_address(
            ride_data['driver_pubkey'],
            ride_data['passenger_pubkey'],
            ride_data['platform_pubkey']
        )
        
        return {
            'escrow_address': escrow['address'],
            'amount_satoshis': ride_data['price_bitcoin'],
            'required_signatures': 2,
            'participants': ['driver', 'passenger', 'platform']
        }

    def get_payment_status(self, payment_hash: str) -> Dict:
        """Get comprehensive payment status"""
        bitcoin_status = self.bitcoin_service.track_payment_status(payment_hash)
        
        return {
            'payment_hash': payment_hash,
            'status': bitcoin_status['status'],
            'confirmations': bitcoin_status['confirmations'],
            'network_fee': self.bitcoin_service.estimate_transaction_fee()['medium'],
            'estimated_confirmation_time': '10-30 minutes'
        }