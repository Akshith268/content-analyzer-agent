#!/usr/bin/env python3
"""
🔥 ContentGuard Pro - SaaS with UPI/Indian Payment Options
Simple payment integration perfect for Indian market
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import json
import time
import hashlib
import qrcode
import io
import base64
from datetime import datetime, timedelta
from smart_analyzer import SmartContentAnalyzer

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'contentguard-pro-secret-key')

# Initialize analyzer
analyzer = SmartContentAnalyzer()

# Enhanced user database with payment tracking
USERS = {
    'demo@contentguard.pro': {
        'password': 'demo123',
        'plan': 'free',
        'analyses_used': 0,
        'analyses_limit': 100,
        'api_key': 'cg_demo_' + hashlib.md5('demo@contentguard.pro'.encode()).hexdigest()[:16],
        'payment_status': 'active',
        'plan_expiry': None,
        'payment_history': [],
        'created_at': datetime.now().isoformat()
    }
}

# Indian pricing in INR
PRICING_PLANS = {
    'free': {'limit': 100, 'price': 0, 'name': 'Free', 'currency': 'INR'},
    'starter': {'limit': 5000, 'price': 299, 'name': 'Starter', 'currency': 'INR'},
    'pro': {'limit': 25000, 'price': 999, 'name': 'Pro', 'currency': 'INR'},
    'business': {'limit': 100000, 'price': 2999, 'name': 'Business', 'currency': 'INR'},
    'enterprise': {'limit': -1, 'price': 9999, 'name': 'Enterprise', 'currency': 'INR'}
}

# UPI payment details (you can update these with your actual UPI details)
UPI_DETAILS = {
    'upi_id': 'contentguard@paytm',  # Replace with your UPI ID
    'merchant_name': 'ContentGuard Pro',
    'phone': '+91-9876543210'  # Replace with your phone number
}

@app.route('/')
def home():
    """Landing page"""
    return render_template('landing.html', pricing_plans=PRICING_PLANS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in USERS and USERS[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email not in USERS:
            USERS[email] = {
                'password': password,
                'plan': 'free',
                'analyses_used': 0,
                'analyses_limit': 100,
                'api_key': 'cg_' + hashlib.md5(email.encode()).hexdigest()[:16],
                'payment_status': 'active',
                'plan_expiry': None,
                'payment_history': [],
                'created_at': datetime.now().isoformat()
            }
            session['user'] = email
            flash('Account created successfully! Welcome to ContentGuard Pro!', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('signup.html', error='Email already exists')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

def generate_upi_qr(amount, plan_name, user_email):
    """Generate UPI QR code for payment"""
    # Create UPI payment URL
    upi_url = f"upi://pay?pa={UPI_DETAILS['upi_id']}&pn={UPI_DETAILS['merchant_name']}&am={amount}&cu=INR&tn=ContentGuard {plan_name} Plan - {user_email}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_code_base64, upi_url

@app.route('/dashboard')
def dashboard():
    """User dashboard with payment info"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if user exists in database
    if session['user'] not in USERS:
        flash('User session expired. Please login again.', 'warning')
        session.pop('user', None)
        return redirect(url_for('login'))
    
    user = USERS[session['user']]
    
    # Calculate usage percentage
    usage_percentage = (user['analyses_used'] / user['analyses_limit']) * 100 if user['analyses_limit'] > 0 else 0
    
    # Check if plan is expiring soon
    plan_warning = None
    if user.get('plan_expiry'):
        expiry_date = datetime.fromisoformat(user['plan_expiry'])
        days_left = (expiry_date - datetime.now()).days
        if days_left <= 5:
            plan_warning = f"Your {user['plan']} plan expires in {days_left} days!"
    
    return render_template('dashboard_india.html', 
                         user=user, 
                         pricing_plans=PRICING_PLANS,
                         usage_percentage=usage_percentage,
                         plan_warning=plan_warning)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_page():
    """Content analysis interface"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if user exists in database
    if session['user'] not in USERS:
        flash('User session expired. Please login again.', 'warning')
        session.pop('user', None)
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form.get('content', '')
        if content:
            user = USERS[session['user']]
            
            # Check if plan is expired
            if user.get('plan_expiry'):
                expiry_date = datetime.fromisoformat(user['plan_expiry'])
                if datetime.now() > expiry_date:
                    user['plan'] = 'free'
                    user['analyses_limit'] = 100
                    flash('Your premium plan has expired. Switched to free plan.', 'warning')
            
            # Check usage limits
            if user['analyses_used'] >= user['analyses_limit'] and user['analyses_limit'] > 0:
                return render_template('analyze.html', 
                                     error='Usage limit reached. Please upgrade your plan to continue.',
                                     upgrade_needed=True,
                                     pricing_plans=PRICING_PLANS)
            
            # Analyze content
            result = analyzer.analyze_content(content)
            
            # Update usage
            user['analyses_used'] += 1
            
            return render_template('analyze.html', result=result, content=content)
    
    return render_template('analyze.html')

@app.route('/payment/<plan>')
def payment_page(plan):
    """Payment page with UPI options"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if user exists in database
    if session['user'] not in USERS:
        flash('User session expired. Please login again.', 'warning')
        session.pop('user', None)
        return redirect(url_for('login'))
    
    if plan not in PRICING_PLANS or plan == 'free':
        flash('Invalid plan selected.', 'error')
        return redirect(url_for('pricing'))
    
    user_email = session['user']
    plan_info = PRICING_PLANS[plan]
    
    # Generate UPI QR code
    qr_code_base64, upi_url = generate_upi_qr(plan_info['price'], plan_info['name'], user_email)
    
    return render_template('payment_upi.html', 
                         plan=plan,
                         plan_info=plan_info,
                         qr_code=qr_code_base64,
                         upi_url=upi_url,
                         upi_details=UPI_DETAILS,
                         user_email=user_email)

@app.route('/create-order', methods=['POST'])
def create_order():
    """Create payment order (supports both UPI and Razorpay)"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        plan = data.get('plan')
        payment_method = data.get('payment_method', 'upi')  # upi or razorpay
        
        if plan not in PRICING_PLANS or plan == 'free':
            return jsonify({'error': 'Invalid plan'}), 400
        
        user_email = session['user']
        plan_info = PRICING_PLANS[plan]
        
        # Generate order ID
        order_id = f"CG_{int(time.time())}_{hashlib.md5(user_email.encode()).hexdigest()[:8]}"
        
        if payment_method == 'razorpay':
            # Razorpay integration (requires API keys)
            # For now, return placeholder - you need to add Razorpay keys to .env
            return jsonify({
                'success': True,
                'order_id': order_id,
                'amount': plan_info['price'] * 100,  # Razorpay expects paise
                'currency': 'INR',
                'payment_method': 'razorpay',
                'key': 'rzp_test_your_key_here',  # Add your Razorpay key
                'message': 'Razorpay integration requires API keys in .env file'
            })
        else:
            # UPI direct payment
            qr_code_base64, upi_url = generate_upi_qr(plan_info['price'], plan_info['name'], user_email)
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'amount': plan_info['price'],
                'currency': 'INR',
                'upi_url': upi_url,
                'qr_code': qr_code_base64,
                'payment_method': 'upi',
                'redirect_url': f"/payment/{plan}"
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment-status')
def payment_status():
    """Check payment status for current user"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user = USERS.get(session['user'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check latest payment status
    payment_history = user.get('payment_history', [])
    if payment_history:
        latest_payment = payment_history[-1]
        return jsonify({
            'status': latest_payment.get('status', 'pending'),
            'plan': user.get('plan', 'free'),
            'transaction_id': latest_payment.get('transaction_id', '')
        })
    
    return jsonify({
        'status': 'no_payments',
        'plan': user.get('plan', 'free')
    })

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Manual payment verification"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if user exists in database
    if session['user'] not in USERS:
        flash('User session expired. Please login again.', 'warning')
        session.pop('user', None)
        return redirect(url_for('login'))
    
    transaction_id = request.form.get('transaction_id', '').strip()
    plan = request.form.get('plan')
    
    if not transaction_id or not plan:
        flash('Please provide transaction ID.', 'error')
        return redirect(url_for('payment_page', plan=plan))
    
    if plan not in PRICING_PLANS:
        flash('Invalid plan.', 'error')
        return redirect(url_for('pricing'))
    
    user = USERS[session['user']]
    plan_info = PRICING_PLANS[plan]
    
    # Add to payment history for manual verification
    payment_record = {
        'transaction_id': transaction_id,
        'plan': plan,
        'amount': plan_info['price'],
        'status': 'pending_verification',
        'submitted_at': datetime.now().isoformat(),
        'verified_at': None
    }
    
    if 'payment_history' not in user:
        user['payment_history'] = []
    
    user['payment_history'].append(payment_record)
    
    flash(f'Payment submitted! Transaction ID: {transaction_id}. We will verify and activate your {plan_info["name"]} plan within 24 hours.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/verify-payments')
def admin_verify_payments():
    """Admin page to verify payments (simple implementation)"""
    # In production, this should have proper admin authentication
    pending_payments = []
    
    for email, user in USERS.items():
        if 'payment_history' in user:
            for payment in user['payment_history']:
                if payment['status'] == 'pending_verification':
                    pending_payments.append({
                        'email': email,
                        'payment': payment
                    })
    
    return render_template('admin_verify.html', pending_payments=pending_payments)

@app.route('/admin/approve-payment', methods=['POST'])
def approve_payment():
    """Approve a payment manually"""
    email = request.form.get('email')
    transaction_id = request.form.get('transaction_id')
    
    if email in USERS:
        user = USERS[email]
        for payment in user.get('payment_history', []):
            if payment['transaction_id'] == transaction_id:
                # Approve payment
                payment['status'] = 'verified'
                payment['verified_at'] = datetime.now().isoformat()
                
                # Update user plan
                plan = payment['plan']
                user['plan'] = plan
                user['analyses_limit'] = PRICING_PLANS[plan]['limit']
                user['payment_status'] = 'active'
                
                # Set expiry date (30 days from now)
                expiry_date = datetime.now() + timedelta(days=30)
                user['plan_expiry'] = expiry_date.isoformat()
                
                flash(f'Payment approved for {email}!', 'success')
                break
    
    return redirect(url_for('admin_verify_payments'))

@app.route('/api/v1/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for content analysis"""
    try:
        # Check API key
        api_key = request.headers.get('X-API-Key') or request.json.get('api_key')
        user_email = None
        
        for email, user_data in USERS.items():
            if user_data['api_key'] == api_key:
                user_email = email
                break
        
        if not user_email:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user = USERS[user_email]
        
        # Check usage limits
        if user['analyses_used'] >= user['analyses_limit'] and user['analyses_limit'] > 0:
            return jsonify({'error': 'Usage limit reached'}), 429
        
        # Get content
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Analyze content
        result = analyzer.analyze_content(content)
        
        # Update usage
        user['analyses_used'] += 1
        
        # Return API response
        response = {
            'success': True,
            'analysis': {
                'decision': result.decision,
                'confidence': result.confidence,
                'reason': result.reason,
                'sentiment': result.sentiment,
                'risk_level': result.risk_level,
                'processing_time': result.processing_time
            },
            'metadata': {
                'patterns_used': result.patterns_used,
                'learning_applied': result.learning_applied,
                'timestamp': datetime.now().isoformat()
            },
            'usage': {
                'analyses_used': user['analyses_used'],
                'analyses_limit': user['analyses_limit'],
                'plan': user['plan']
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/stats')
def api_stats():
    """API endpoint for user statistics"""
    api_key = request.headers.get('X-API-Key')
    user_email = None
    
    for email, user_data in USERS.items():
        if user_data['api_key'] == api_key:
            user_email = email
            break
    
    if not user_email:
        return jsonify({'error': 'Invalid API key'}), 401
    
    user = USERS[user_email]
    stats = {
        'analyses_used': user['analyses_used'],
        'analyses_limit': user['analyses_limit'],
        'plan': user['plan'],
        'usage_percentage': (user['analyses_used'] / user['analyses_limit']) * 100 if user['analyses_limit'] > 0 else 0
    }
    
    return jsonify(stats)

@app.route('/pricing')
def pricing():
    """Pricing page with Indian pricing"""
    return render_template('pricing_india.html', pricing_plans=PRICING_PLANS)

@app.route('/docs')
def api_docs():
    """API documentation"""
    return render_template('api_docs.html')

# Update the upgrade route to redirect to payment page
@app.route('/upgrade/<plan>')
def upgrade_plan(plan):
    """Redirect to payment page for plan upgrade"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if plan == 'free':
        # Downgrade is allowed without payment
        user = USERS[session['user']]
        user['plan'] = 'free'
        user['analyses_limit'] = 100
        user['plan_expiry'] = None
        flash('Switched to free plan.', 'info')
        return redirect(url_for('dashboard'))
    
    if plan not in PRICING_PLANS:
        flash('Invalid plan selected.', 'error')
        return redirect(url_for('pricing'))
    
    # Redirect to payment page
    return redirect(url_for('payment_page', plan=plan))

if __name__ == '__main__':
    print("🚀 Starting ContentGuard Pro SaaS Platform...")
    print("🌐 Web Interface: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/docs")
    print("🔑 Demo Login: demo@contentguard.pro / demo123")
    app.run(debug=True, host='0.0.0.0', port=5000)
