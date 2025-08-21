#!/usr/bin/env python3
"""
🔥 ContentGuard Pro - Business SaaS with Razorpay (India)
Real payment integration for Indian market
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import json
import time
import hashlib
import razorpay
import hmac
from datetime import datetime, timedelta
from smart_analyzer import SmartContentAnalyzer

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'contentguard-pro-secret-key')

# Configure Razorpay
razorpay_client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET')))
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')

# Initialize analyzer
analyzer = SmartContentAnalyzer()

# Enhanced user database with payment tracking
USERS = {
    'demo@contentguard.pro': {
        'password': 'demo123',
        'plan': 'free',
        'analyses_used': 15,
        'analyses_limit': 100,
        'api_key': 'cg_demo_' + hashlib.md5('demo@contentguard.pro'.encode()).hexdigest()[:16],
        'razorpay_customer_id': None,
        'subscription_id': None,
        'subscription_status': 'active',
        'subscription_end_date': None,
        'created_at': datetime.now().isoformat()
    }
}

# Pricing plans with INR pricing (Indian market)
PRICING_PLANS = {
    'free': {
        'limit': 100, 
        'price': 0, 
        'name': 'Free', 
        'currency': 'INR',
        'features': ['100 analyses/month', 'API access', 'Learning AI', 'Email support']
    },
    'pro': {
        'limit': 10000, 
        'price': 1999, 
        'name': 'Pro', 
        'currency': 'INR',
        'features': ['10,000 analyses/month', 'Priority API', 'Advanced AI', 'Priority support', 'Analytics dashboard']
    },
    'business': {
        'limit': 100000, 
        'price': 7999, 
        'name': 'Business', 
        'currency': 'INR',
        'features': ['1,00,000 analyses/month', 'Dedicated API', 'Custom AI training', '24/7 support', 'Team management', 'Integrations']
    },
    'enterprise': {
        'limit': -1, 
        'price': 19999, 
        'name': 'Enterprise', 
        'currency': 'INR',
        'features': ['Unlimited analyses', 'White-label options', 'Dedicated models', 'Dedicated support', 'Custom integrations', 'SLA guarantee']
    }
}

@app.route('/')
def home():
    """Landing page"""
    return render_template('landing_india.html', pricing_plans=PRICING_PLANS)

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
    """User registration with Razorpay customer creation"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', email.split('@')[0])
        
        if email not in USERS:
            try:
                # Create Razorpay customer
                customer_data = {
                    'name': name,
                    'email': email,
                    'contact': request.form.get('phone', ''),
                    'notes': {
                        'source': 'contentguard_signup',
                        'plan': 'free'
                    }
                }
                customer = razorpay_client.customer.create(customer_data)
                
                USERS[email] = {
                    'password': password,
                    'name': name,
                    'plan': 'free',
                    'analyses_used': 0,
                    'analyses_limit': 100,
                    'api_key': 'cg_' + hashlib.md5(email.encode()).hexdigest()[:16],
                    'razorpay_customer_id': customer['id'],
                    'subscription_id': None,
                    'subscription_status': 'active',
                    'subscription_end_date': None,
                    'created_at': datetime.now().isoformat()
                }
                session['user'] = email
                flash('Account created successfully! Welcome to ContentGuard Pro!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                return render_template('signup.html', error=f'Registration failed: {str(e)}')
        else:
            return render_template('signup.html', error='Email already exists')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """User dashboard with subscription info"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = USERS[session['user']]
    
    # Calculate usage percentage
    usage_percentage = 0
    if user['analyses_limit'] > 0:
        usage_percentage = (user['analyses_used'] / user['analyses_limit']) * 100
    
    # Get subscription info
    subscription_info = None
    if user.get('subscription_id'):
        try:
            subscription = razorpay_client.subscription.fetch(user['subscription_id'])
            subscription_info = {
                'status': subscription['status'],
                'current_end': datetime.fromtimestamp(subscription.get('current_end', 0)) if subscription.get('current_end') else None,
                'next_billing': datetime.fromtimestamp(subscription.get('current_end', 0)) if subscription.get('current_end') else None
            }
        except Exception:
            subscription_info = None
    
    return render_template('dashboard_india.html', 
                         user=user, 
                         pricing_plans=PRICING_PLANS, 
                         subscription_info=subscription_info,
                         usage_percentage=usage_percentage)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_page():
    """Content analysis interface"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form.get('content', '')
        if content:
            user = USERS[session['user']]
            
            # Check usage limits
            if user['analyses_used'] >= user['analyses_limit'] and user['analyses_limit'] > 0:
                return render_template('analyze.html', 
                                     error='🚫 Usage limit reached! Please upgrade your plan to continue.',
                                     upgrade_needed=True,
                                     current_plan=user['plan'],
                                     pricing_plans=PRICING_PLANS)
            
            # Analyze content
            result = analyzer.analyze_content(content)
            
            # Update usage
            user['analyses_used'] += 1
            
            return render_template('analyze.html', result=result, content=content)
    
    return render_template('analyze.html')

@app.route('/create-order', methods=['POST'])
def create_order():
    """Create Razorpay order for subscription"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        plan = request.json.get('plan')
        user = USERS[session['user']]
        
        if plan not in PRICING_PLANS or plan == 'free':
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan_info = PRICING_PLANS[plan]
        amount = plan_info['price'] * 100  # Razorpay expects amount in paise
        
        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'order_{user["api_key"]}_{int(time.time())}',
            'notes': {
                'user_email': session['user'],
                'plan': plan,
                'plan_name': plan_info['name']
            }
        }
        
        order = razorpay_client.order.create(order_data)
        
        return jsonify({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'key': RAZORPAY_KEY_ID,
            'name': 'ContentGuard Pro',
            'description': f'{plan_info["name"]} Plan - ₹{plan_info["price"]}/month',
            'prefill': {
                'name': user.get('name', session['user'].split('@')[0]),
                'email': session['user']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and activate subscription"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        data = request.json
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        plan = data.get('plan')
        
        # Verify signature
        generated_signature = hmac.new(
            os.getenv('RAZORPAY_KEY_SECRET').encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature == razorpay_signature:
            # Payment verified successfully
            user = USERS[session['user']]
            
            # Update user subscription
            user['plan'] = plan
            user['analyses_limit'] = PRICING_PLANS[plan]['limit']
            user['subscription_status'] = 'active'
            user['subscription_end_date'] = (datetime.now() + timedelta(days=30)).isoformat()
            
            # Store payment info (in real app, save to database)
            user['last_payment'] = {
                'payment_id': razorpay_payment_id,
                'order_id': razorpay_order_id,
                'amount': PRICING_PLANS[plan]['price'],
                'date': datetime.now().isoformat(),
                'plan': plan
            }
            
            flash(f'🎉 Successfully upgraded to {PRICING_PLANS[plan]["name"]} plan!', 'success')
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'error': 'Payment verification failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/razorpay-webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhook events"""
    webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    
    if webhook_secret and webhook_signature:
        try:
            # Verify webhook signature
            expected_signature = hmac.new(
                webhook_secret.encode(),
                request.get_data(),
                hashlib.sha256
            ).hexdigest()
            
            if expected_signature != webhook_signature:
                return 'Invalid signature', 400
                
        except Exception:
            return 'Webhook verification failed', 400
    
    # Process webhook event
    event = request.json
    
    if event.get('event') == 'payment.captured':
        # Handle successful payment
        payment = event['payload']['payment']['entity']
        # Update subscription status in database
        
    elif event.get('event') == 'subscription.charged':
        # Handle subscription renewal
        subscription = event['payload']['subscription']['entity']
        # Extend subscription period
    
    return jsonify({'status': 'success'})

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
        
        # Check subscription status
        if user.get('subscription_status') == 'cancelled':
            return jsonify({
                'error': 'Subscription cancelled. Please reactivate to continue.',
                'upgrade_url': f"{request.host_url}pricing"
            }), 402
        
        # Check usage limits
        if user['analyses_used'] >= user['analyses_limit'] and user['analyses_limit'] > 0:
            return jsonify({
                'error': 'Usage limit reached. Please upgrade your plan.',
                'current_plan': user['plan'],
                'analyses_used': user['analyses_used'],
                'analyses_limit': user['analyses_limit'],
                'upgrade_url': f"{request.host_url}pricing"
            }), 429
        
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
                'timestamp': datetime.now().isoformat(),
                'api_version': 'v1'
            },
            'usage': {
                'analyses_used': user['analyses_used'],
                'analyses_limit': user['analyses_limit'],
                'plan': user['plan'],
                'remaining': max(0, user['analyses_limit'] - user['analyses_used']) if user['analyses_limit'] > 0 else 'unlimited'
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
        'subscription_status': user.get('subscription_status', 'active'),
        'usage_percentage': (user['analyses_used'] / user['analyses_limit']) * 100 if user['analyses_limit'] > 0 else 0,
        'remaining_analyses': max(0, user['analyses_limit'] - user['analyses_used']) if user['analyses_limit'] > 0 else 'unlimited'
    }
    
    return jsonify(stats)

@app.route('/pricing')
def pricing():
    """Pricing page with Razorpay integration"""
    return render_template('pricing_india.html', 
                         pricing_plans=PRICING_PLANS, 
                         razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/docs')
def api_docs():
    """API documentation"""
    return render_template('api_docs.html')

@app.route('/billing')
def billing():
    """Billing and payment history"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = USERS[session['user']]
    return render_template('billing.html', user=user, pricing_plans=PRICING_PLANS)

# Keep upgrade route for free plan downgrades
@app.route('/upgrade/<plan>')
def upgrade_plan(plan):
    """Handle plan changes"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if plan == 'free':
        # Downgrade is allowed without payment
        user = USERS[session['user']]
        user['plan'] = 'free'
        user['analyses_limit'] = 100
        user['subscription_status'] = 'active'
        flash('Downgraded to free plan.', 'info')
        return redirect(url_for('dashboard'))
    
    # For paid plans, redirect to pricing page
    flash('Complete payment to upgrade your plan.', 'info')
    return redirect(url_for('pricing'))

if __name__ == '__main__':
    print("🔥 Starting ContentGuard Pro - India Business Edition...")
    print("💳 Razorpay Payment Integration: ENABLED")
    print("🇮🇳 Indian Market Optimized (INR Pricing)")
    print("🌐 Web Interface: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/docs")
    print("🔑 Demo Login: demo@contentguard.pro / demo123")
    print("")
    print("⚠️  SETUP REQUIRED:")
    print("1. Get Razorpay keys: https://dashboard.razorpay.com/#/app/keys")
    print("2. Update .env with RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET")
    print("3. Enable webhooks in Razorpay Dashboard")
    print("4. Test with Razorpay test cards")
    print("")
    print("💰 Pricing (INR):")
    for plan, details in PRICING_PLANS.items():
        if details['price'] > 0:
            print(f"   {details['name']}: ₹{details['price']}/month")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
