import requests
import json
import os
from decimal import Decimal

class BitcoinService:
    def __init__(self):
        self.rpc_host = os.getenv('BITCOIN_RPC_HOST', 'localhost')
        self.rpc_port = os.getenv('BITCOIN_RPC_PORT', '8332')
        self.rpc_user = os.getenv('BITCOIN_RPC_USER')
        self.rpc_password = os.getenv('BITCOIN_RPC_PASSWORD')
        self.rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.rpc_host}:{self.rpc_port}/"

    def rpc_call(self, method, params=None):
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

    def get_bitcoin_price_usd(self):
        """Get current Bitcoin price in USD from a public API"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
            data = response.json()
            return data['bitcoin']['usd']
        except:
            return 45000  # Fallback price

    def convert_usd_to_satoshis(self, usd_amount):
        """Convert USD amount to satoshis"""
        btc_price = self.get_bitcoin_price_usd()
        btc_amount = usd_amount / btc_price
        satoshis = int(btc_amount * 100000000)  # Convert to satoshis
        return satoshis

    def create_payment_request(self, amount_usd, recipient_address):
        """Create a Bitcoin payment request"""
        satoshis = self.convert_usd_to_satoshis(amount_usd)
        
        return {
            'recipient_address': recipient_address,
            'amount_satoshis': satoshis,
            'amount_btc': satoshis / 100000000,
            'amount_usd': amount_usd,
            'btc_price': self.get_bitcoin_price_usd()
        }

    def generate_new_address(self, label="rideshare"):
        """Generate a new Bitcoin address for receiving payments"""
        result = self.rpc_call("getnewaddress", [label])
        if "error" not in result and "result" in result:
            return result["result"]
        return None

    def validate_address(self, address):
        """Validate Bitcoin address"""
        result = self.rpc_call("validateaddress", [address])
        if "error" not in result and "result" in result:
            return result["result"]["isvalid"]
        return False

    def get_transaction_info(self, txid):
        """Get transaction information"""
        result = self.rpc_call("gettransaction", [txid])
        if "error" not in result and "result" in result:
            return result["result"]
        return None

    def send_bitcoin(self, to_address, amount_btc):
        """Send Bitcoin (for testing purposes - be careful with this in production)"""
        result = self.rpc_call("sendtoaddress", [to_address, amount_btc])
        if "error" not in result and "result" in result:
            return result["result"]  # Returns transaction ID
        return None

    def get_wallet_balance(self):
        """Get wallet balance"""
        result = self.rpc_call("getbalance")
        if "error" not in result and "result" in result:
            return result["result"]
        return 0

# Lightning Network Service (for future implementation)
class LightningService:
    def __init__(self):
        # This would connect to LND or c-lightning
        pass
    
    def create_invoice(self, amount_satoshis, memo="RideShare payment"):
        """Create Lightning invoice"""
        # Implementation would depend on Lightning implementation (LND, c-lightning, etc.)
        pass
    
    def pay_invoice(self, payment_request):
        """Pay Lightning invoice"""
        # Implementation for paying Lightning invoices
        pass

# Bitcoin price tracking
def get_realtime_btc_price():
    """Get real-time Bitcoin price from multiple sources"""
    sources = [
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
    ]
    
    for source in sources:
        try:
            if "coingecko" in source:
                response = requests.get(source)
                data = response.json()
                return data['bitcoin']['usd']
            elif "coindesk" in source:
                response = requests.get(source)
                data = response.json()
                return float(data['bpi']['USD']['rate_float'])
        except:
            continue
    
    return 45000  # Fallback price