"""
Bitcoin Testnet Payment Integration
Generates testnet addresses and QR codes for testing payments
"""
import qrcode
import io
import base64
import requests
from datetime import datetime

class BitcoinTestnetPayment:
    """Simple Bitcoin testnet payment handler"""

    def __init__(self):
        self.testnet_api = "https://blockstream.info/testnet/api"

    def generate_payment_qr(self, address, amount_btc):
        """
        Generate QR code for Bitcoin payment
        Returns base64 encoded image
        """
        # Bitcoin URI format: bitcoin:address?amount=X&label=RideSharePayment
        bitcoin_uri = f"bitcoin:{address}?amount={amount_btc}&label=RideShare Payment"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(bitcoin_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str

    def check_address_balance(self, address):
        """Check testnet address balance using Blockstream API"""
        try:
            response = requests.get(f"{self.testnet_api}/address/{address}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'balance': data.get('chain_stats', {}).get('funded_txo_sum', 0),
                    'received': data.get('chain_stats', {}).get('funded_txo_sum', 0),
                    'tx_count': data.get('chain_stats', {}).get('tx_count', 0)
                }
        except Exception as e:
            print(f"Error checking balance: {e}")
        return None

    def check_transaction(self, txid):
        """Check if a transaction is confirmed"""
        try:
            response = requests.get(f"{self.testnet_api}/tx/{txid}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'confirmed': data.get('status', {}).get('confirmed', False),
                    'block_height': data.get('status', {}).get('block_height'),
                    'confirmations': data.get('status', {}).get('confirmations', 0)
                }
        except Exception as e:
            print(f"Error checking transaction: {e}")
        return None

    def verify_payment(self, address, expected_amount_sat, min_confirmations=1):
        """
        Verify if payment has been received
        Returns transaction details if payment is found
        """
        try:
            response = requests.get(f"{self.testnet_api}/address/{address}/txs")
            if response.status_code == 200:
                transactions = response.json()

                for tx in transactions:
                    # Check outputs going to this address
                    for vout in tx.get('vout', []):
                        if vout.get('scriptpubkey_address') == address:
                            amount = vout.get('value', 0)
                            confirmations = tx.get('status', {}).get('confirmations', 0)

                            # Check if amount matches and has enough confirmations
                            if amount >= expected_amount_sat and confirmations >= min_confirmations:
                                return {
                                    'txid': tx.get('txid'),
                                    'amount': amount,
                                    'confirmations': confirmations,
                                    'confirmed': confirmations >= min_confirmations,
                                    'timestamp': tx.get('status', {}).get('block_time')
                                }
        except Exception as e:
            print(f"Error verifying payment: {e}")

        return None

# Testnet faucets for testing:
TESTNET_FAUCETS = [
    "https://testnet-faucet.mempool.co/",
    "https://bitcoinfaucet.uo1.net/",
    "https://testnet.help/en/btcfaucet/testnet",
    "https://coinfaucet.eu/en/btc-testnet/"
]
