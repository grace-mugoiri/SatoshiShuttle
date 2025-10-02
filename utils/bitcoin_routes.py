from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.enhanced_bitcoin import (
    EnhancedBitcoinService, 
    LightningNetworkService,
    RideShareBitcoinIntegration,
    calculate_ride_pricing,
    format_satoshis
)
import time

# Create Blueprint
bitcoin_bp = Blueprint('bitcoin', __name__, url_prefix='/api/bitcoin')

# Initialize services
bitcoin_service = EnhancedBitcoinService()
lightning_service = LightningNetworkService()
rideshare_integration = RideShareBitcoinIntegration()

@bitcoin_bp.route('/price', methods=['GET'])
def get_bitcoin_price():
    """Get current Bitcoin price from multiple sources"""
    try:
        prices = bitcoin_service.get_bitcoin_price_multiple_sources()
        fees = bitcoin_service.estimate_transaction_fee()
        
        # Get the primary price source
        primary_source = list(prices.keys())[0]
        primary_prices = prices[primary_source]
        
        return jsonify({
            'prices': primary_prices,
            'source': primary_source,
            'fees': fees,
            'last_updated': int(time.time())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bitcoin_bp.route('/convert', methods=['POST'])
def convert_currency():
    """Convert currency to Bitcoin/Satoshis"""
    try:
        data = request.get_json()
        amount = float(data['amount'])
        from_currency = data.get('from_currency', 'usd')
        
        satoshis = bitcoin_service.convert_currency_to_satoshis(amount, from_currency)
        
        return jsonify({
            'original_amount': amount,
            'original_currency': from_currency,
            'satoshis': satoshis,
            'btc': satoshis / 100000000,
            'formatted': format_satoshis(satoshis)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/validate-address', methods=['POST'])
def validate_address():
    """Validate Bitcoin address"""
    try:
        data = request.get_json()
        address = data['address']
        
        validation_result = bitcoin_service.validate_bitcoin_address(address)
        
        return jsonify(validation_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/estimate-ride-price', methods=['POST'])
def estimate_ride_price():
    """Estimate ride price in multiple currencies"""
    try:
        data = request.get_json()
        distance_km = float(data['distance_km'])
        base_rate = float(data.get('base_rate_per_km', 0.5))
        
        pricing = calculate_ride_pricing(distance_km, base_rate)
        
        return jsonify(pricing)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/create-payment', methods=['POST'])
@jwt_required()
def create_payment():
    """Create Bitcoin payment for ride"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get ride information
        ride_id = data['ride_id']
        payment_method = data.get('payment_method', 'bitcoin')
        
        # This would typically fetch ride data from database
        ride_data = {
            'ride_id': ride_id,
            'passenger_id': user_id,
            'price_bitcoin': data['amount_satoshis'],
            'driver_bitcoin_address': data['recipient_address'],
            'origin': data.get('origin', 'Unknown'),
            'destination': data.get('destination', 'Unknown')
        }
        
        payment_data = rideshare_integration.process_ride_payment(ride_data, payment_method)
        
        return jsonify({
            'payment_id': f"payment_{int(time.time())}_{user_id}",
            'payment_data': payment_data,
            'created_at': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/lightning/create-invoice', methods=['POST'])
@jwt_required()
def create_lightning_invoice():
    """Create Lightning Network invoice"""
    try:
        data = request.get_json()
        amount_satoshis = int(data['amount_satoshis'])
        memo = data.get('memo', 'RideShare Payment')
        
        invoice = lightning_service.create_invoice(amount_satoshis, memo)
        
        return jsonify({
            'invoice': invoice,
            'qr_data': f"lightning:{invoice['payment_request']}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/lightning/pay-invoice', methods=['POST'])
@jwt_required()
def pay_lightning_invoice():
    """Pay Lightning Network invoice"""
    try:
        data = request.get_json()
        payment_request = data['payment_request']
        
        payment_result = lightning_service.pay_invoice(payment_request)
        
        return jsonify(payment_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/payment-status/<payment_hash>', methods=['GET'])
def get_payment_status(payment_hash):
    """Get payment status"""
    try:
        status = rideshare_integration.get_payment_status(payment_hash)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/create-escrow', methods=['POST'])
@jwt_required()
def create_escrow():
    """Create escrow payment for ride"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        ride_data = {
            'driver_pubkey': data['driver_pubkey'],
            'passenger_pubkey': data['passenger_pubkey'],
            'platform_pubkey': data.get('platform_pubkey', 'default_platform_key'),
            'price_bitcoin': data['amount_satoshis']
        }
        
        escrow_data = rideshare_integration.setup_escrow_payment(ride_data)
        
        return jsonify({
            'escrow_id': f"escrow_{int(time.time())}_{user_id}",
            'escrow_data': escrow_data,
            'instructions': 'Send Bitcoin to the escrow address. Funds will be released when ride is completed.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/fee-estimate', methods=['GET'])
def get_fee_estimate():
    """Get current Bitcoin network fee estimates"""
    try:
        fees = bitcoin_service.estimate_transaction_fee()
        
        # Calculate fees for different transaction sizes
        transaction_sizes = {
            'simple': 250,  # Single input, single output
            'standard': 400,  # Multiple inputs/outputs
            'complex': 600   # Many inputs/outputs
        }
        
        fee_estimates = {}
        for priority, fee_rate in fees.items():
            fee_estimates[priority] = {}
            for tx_type, size in transaction_sizes.items():
                fee_estimates[priority][tx_type] = {
                    'satoshis': fee_rate * size,
                    'btc': (fee_rate * size) / 100000000,
                    'usd_approx': ((fee_rate * size) / 100000000) * bitcoin_service.get_bitcoin_price_multiple_sources()[list(bitcoin_service.get_bitcoin_price_multiple_sources().keys())[0]]['usd']
                }
        
        return jsonify({
            'fee_rates': fees,
            'estimates': fee_estimates,
            'updated_at': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bitcoin_bp.route('/generate-qr', methods=['POST'])
def generate_payment_qr():
    """Generate QR code data for Bitcoin payment"""
    try:
        data = request.get_json()
        address = data['address']
        amount_btc = float(data.get('amount_btc', 0))
        label = data.get('label', 'RideShare Payment')
        
        # Validate address first
        validation = bitcoin_service.validate_bitcoin_address(address)
        if not validation['valid']:
            return jsonify({'error': 'Invalid Bitcoin address'}), 400
        
        qr_data = bitcoin_service.create_payment_qr_data(address, amount_btc, label)
        
        return jsonify({
            'qr_data': qr_data,
            'address': address,
            'amount_btc': amount_btc,
            'label': label,
            'address_type': validation['type']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/price-alerts', methods=['POST'])
@jwt_required()
def create_price_alert():
    """Create Bitcoin price alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        target_price = float(data['target_price'])
        alert_type = data.get('alert_type', 'above')
        
        alert = rideshare_integration.price_alert_service.add_price_alert(
            user_id, target_price, alert_type
        )
        
        return jsonify({
            'alert_id': f"alert_{int(time.time())}_{user_id}",
            'alert': alert,
            'message': f'Price alert created: Notify when Bitcoin goes {alert_type} ${target_price}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bitcoin_bp.route('/price-trend', methods=['GET'])
def get_price_trend():
    """Get Bitcoin price trend analysis"""
    try:
        hours = int(request.args.get('hours', 24))
        trend = rideshare_integration.price_alert_service.get_price_trend(hours)
        
        return jsonify({
            'trend_analysis': trend,
            'current_time': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bitcoin_bp.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    """Handle payment webhooks from Bitcoin payment processors"""
    try:
        data = request.get_json()
        
        # Verify webhook signature if needed
        signature = request.headers.get('X-Webhook-Signature')
        
        # Process payment notification
        payment_hash = data.get('payment_hash')
        status = data.get('status')
        amount_received = data.get('amount_received')
        
        # Update payment status in database
        # This would typically update the booking/payment record
        
        return jsonify({
            'received': True,
            'payment_hash': payment_hash,
            'status': status,
            'processed_at': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Error handlers
@bitcoin_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Bitcoin API endpoint not found'}), 404

@bitcoin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Bitcoin service internal error'}), 500