#!/usr/bin/env python3
"""
🔥 ContentGuard Pro - Business-Level SaaS with Stripe Payments
Real payment integration for subscription management
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import json
import time
import hashlib
import stripe
from datetime import datetime, timedelta
from smart_analyzer import SmartContentAnalyzer

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'contentguard-pro-secret-key')

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

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
        'stripe_customer_id': None,
        'subscription_id': None,
        'subscription_status': 'active',
        'trial_end': None,
        'created_at': datetime.now().isoformat()
    }
}

# Stripe Price IDs (you'll need to create these in Stripe Dashboard)
STRIPE_PRICES = {
    'pro': 'price_pro_monthly_29',  # Replace with actual Stripe price ID
    'business': 'price_business_monthly_99',  # Replace with actual Stripe price ID
    'enterprise': 'price_enterprise_monthly_299'  # Replace with actual Stripe price ID
}

# Pricing plans with Stripe integration
PRICING_PLANS = {
    'free': {'limit': 100, 'price': 0, 'name': 'Free', 'stripe_price_id': None},
    'pro': {'limit': 10000, 'price': 29, 'name': 'Pro', 'stripe_price_id': STRIPE_PRICES['pro']},
    'business': {'limit': 100000, 'price': 99, 'name': 'Business', 'stripe_price_id': STRIPE_PRICES['business']},
    'enterprise': {'limit': -1, 'price': 299, 'name': 'Enterprise', 'stripe_price_id': STRIPE_PRICES['enterprise']}
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
    """User registration with Stripe customer creation"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email not in USERS:
            try:
                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=email,
                    metadata={'source': 'contentguard_signup'}
                )
                
                USERS[email] = {
                    'password': password,
                    'plan': 'free',
                    'analyses_used': 0,
                    'analyses_limit': 100,
                    'api_key': 'cg_' + hashlib.md5(email.encode()).hexdigest()[:16],
                    'stripe_customer_id': customer.id,
                    'subscription_id': None,
                    'subscription_status': 'active',
                    'trial_end': None,
                    'created_at': datetime.now().isoformat()
                }
                session['user'] = email
                flash('Account created successfully!', 'success')
                return redirect(url_for('dashboard'))
            except stripe.error.StripeError as e:
                return render_template('signup.html', error=f'Payment setup failed: {str(e)}')
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
    
    # Get subscription info from Stripe if exists
    subscription_info = None
    if user.get('subscription_id'):
        try:
            subscription = stripe.Subscription.retrieve(user['subscription_id'])
            subscription_info = {
                'status': subscription.status,
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'cancel_at_period_end': subscription.cancel_at_period_end
            }
        except stripe.error.StripeError:
            subscription_info = None
    
    return render_template('dashboard.html', user=user, pricing_plans=PRICING_PLANS, subscription_info=subscription_info)

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
                                     error='Usage limit reached. Please upgrade your plan.',
                                     upgrade_needed=True)
            
            # Analyze content
            result = analyzer.analyze_content(content)
            
            # Update usage
            user['analyses_used'] += 1
            
            return render_template('analyze.html', result=result, content=content)
    
    return render_template('analyze.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session for subscription"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    try:
        plan = request.json.get('plan')
        user = USERS[session['user']]
        
        if plan not in PRICING_PLANS or plan == 'free':
            return jsonify({'error': 'Invalid plan'}), 400
        
        stripe_price_id = PRICING_PLANS[plan]['stripe_price_id']
        
        checkout_session = stripe.checkout.Session.create(
            customer=user['stripe_customer_id'],
            payment_method_types=['card'],
            line_items=[{
                'price': stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('pricing', _external=True),
            metadata={
                'user_email': session['user'],
                'plan': plan
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/subscription-success')
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid session', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status == 'paid':
            # Update user subscription
            user_email = checkout_session.metadata['user_email']
            plan = checkout_session.metadata['plan']
            
            if user_email in USERS:
                user = USERS[user_email]
                user['plan'] = plan
                user['analyses_limit'] = PRICING_PLANS[plan]['limit']
                user['subscription_id'] = checkout_session.subscription
                user['subscription_status'] = 'active'
                
                flash(f'Successfully upgraded to {PRICING_PLANS[plan]["name"]} plan!', 'success')
            
        return redirect(url_for('dashboard'))
        
    except stripe.error.StripeError as e:
        flash(f'Subscription error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel user subscription"""
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user = USERS[session['user']]
    
    if not user.get('subscription_id'):
        return jsonify({'error': 'No active subscription'}), 400
    
    try:
        # Cancel at period end (don't immediately cancel)
        stripe.Subscription.modify(
            user['subscription_id'],
            cancel_at_period_end=True
        )
        
        flash('Subscription will be cancelled at the end of your billing period.', 'info')
        return jsonify({'success': True})
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle subscription events
    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        # Update user subscription status in database
        # This is where you'd update your actual database
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Downgrade user to free plan
        # This is where you'd update your actual database
    
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
        if user.get('subscription_status') == 'canceled':
            return jsonify({'error': 'Subscription cancelled. Please reactivate to continue.'}), 402
        
        # Check usage limits
        if user['analyses_used'] >= user['analyses_limit'] and user['analyses_limit'] > 0:
            return jsonify({
                'error': 'Usage limit reached',
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
        'subscription_status': user.get('subscription_status', 'active'),
        'usage_percentage': (user['analyses_used'] / user['analyses_limit']) * 100 if user['analyses_limit'] > 0 else 0
    }
    
    return jsonify(stats)

@app.route('/pricing')
def pricing():
    """Pricing page with Stripe integration"""
    return render_template('pricing_stripe.html', 
                         pricing_plans=PRICING_PLANS, 
                         stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route('/docs')
def api_docs():
    """API documentation"""
    return render_template('api_docs.html')

# Keep the old upgrade route for backwards compatibility, but redirect to payment
@app.route('/upgrade/<plan>')
def upgrade_plan(plan):
    """Redirect to payment flow"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if plan == 'free':
        # Downgrade is allowed without payment
        user = USERS[session['user']]
        user['plan'] = 'free'
        user['analyses_limit'] = 100
        flash('Downgraded to free plan.', 'info')
        return redirect(url_for('dashboard'))
    
    # For paid plans, redirect to pricing page
    flash('Please complete payment to upgrade your plan.', 'info')
    return redirect(url_for('pricing'))

if __name__ == '__main__':
    print("🔥 Starting ContentGuard Pro - Business SaaS Platform...")
    print("💳 Stripe Payment Integration: ENABLED")
    print("🌐 Web Interface: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/docs")
    print("🔑 Demo Login: demo@contentguard.pro / demo123")
    print("")
    print("⚠️  SETUP REQUIRED:")
    print("1. Get Stripe keys: https://dashboard.stripe.com/apikeys")
    print("2. Update .env with STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY")
    print("3. Create price objects in Stripe Dashboard")
    print("4. Update STRIPE_PRICES in web_app_business.py")
    app.run(debug=True, host='0.0.0.0', port=5000)
