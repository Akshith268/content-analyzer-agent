// Add this JavaScript to pricing_india.html to fix loading issues

function initiatePayment(plan) {
    // Show loading state
    const button = document.querySelector(`[onclick="initiatePayment('${plan}')"]`);
    const spinner = document.getElementById(`loading-${plan}`);
    const icon = document.getElementById(`icon-${plan}`);
    const text = document.getElementById(`text-${plan}`);
    
    // Update button state
    button.disabled = true;
    spinner.classList.remove('d-none');
    icon.classList.add('d-none');
    text.textContent = 'Redirecting to Payment...';
    
    // Redirect to payment page
    setTimeout(() => {
        window.location.href = `/payment/${plan}`;
    }, 1000);
}

// Auto-check payment status every 30 seconds
function checkPaymentStatus() {
    fetch('/api/payment-status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'verified') {
                window.location.href = '/dashboard';
            }
        })
        .catch(error => console.log('Status check failed'));
}

// Start checking payment status if on payment page
if (window.location.pathname.includes('/payment/')) {
    setInterval(checkPaymentStatus, 30000); // Check every 30 seconds
}
