/**
 * Ticket Mania - Simulated Payment Gateway Controller
 * UPI QR generator, Mock card validator, Success/Failure simulation
 */

document.addEventListener('DOMContentLoaded', () => {
  let selectedMethod = 'UPI';
  const methodTabs = document.querySelectorAll('.payment-method-tab');
  const methodPanels = document.querySelectorAll('.payment-method-panel');
  const payBtn = document.getElementById('submitPaymentBtn');
  const failureToggle = document.getElementById('simulateFailureToggle');
  const paymentAlert = document.getElementById('paymentErrorAlert');
  const processingModalEl = document.getElementById('paymentProcessingModal');
  const processingModal = processingModalEl ? new bootstrap.Modal(processingModalEl, { backdrop: 'static', keyboard: false }) : null;

  // Switch Tabs
  methodTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      methodTabs.forEach(t => t.classList.remove('active'));
      methodPanels.forEach(p => p.classList.add('d-none'));

      tab.classList.add('active');
      selectedMethod = tab.getAttribute('data-method');
      const targetPanel = document.getElementById(`panel-${selectedMethod.toLowerCase()}`);
      if (targetPanel) targetPanel.classList.remove('d-none');
    });
  });

  // Card input formatters
  const cardNumberInput = document.getElementById('cardNumber');
  if (cardNumberInput) {
    cardNumberInput.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '').substring(0, 16);
      val = val.replace(/(.{4})/g, '$1 ').trim();
      e.target.value = val;
    });
  }

  const cardExpiryInput = document.getElementById('cardExpiry');
  if (cardExpiryInput) {
    cardExpiryInput.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '').substring(0, 4);
      if (val.length >= 2) {
        val = val.substring(0, 2) + '/' + val.substring(2);
      }
      e.target.value = val;
    });
  }

  // Handle Simulated Payment Submission
  if (payBtn) {
    payBtn.addEventListener('click', async () => {
      const showId = parseInt(payBtn.getAttribute('data-show-id'), 10);
      const seatsDataStr = payBtn.getAttribute('data-seats');
      const seats = JSON.parse(seatsDataStr || '[]');

      const nameInput = document.getElementById('customerName');
      const emailInput = document.getElementById('customerEmail');
      const phoneInput = document.getElementById('customerPhone');

      const name = nameInput ? nameInput.value.trim() : 'Demo Guest';
      const email = emailInput ? emailInput.value.trim() : 'guest@ticketmania.com';
      const phone = phoneInput ? phoneInput.value.trim() : '9876543210';

      if (!name || !email) {
        if (paymentAlert) {
          paymentAlert.textContent = 'Please fill in your name and email address to receive your demo tickets.';
          paymentAlert.classList.remove('d-none');
        }
        return;
      }

      if (paymentAlert) paymentAlert.classList.add('d-none');

      // Show processing spinner
      if (processingModal) processingModal.show();

      const simulateFailure = failureToggle ? failureToggle.checked : false;

      // Realistic 1.2s delay to simulate bank communication
      setTimeout(async () => {
        try {
          const response = await fetch('/api/process-payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              show_id: showId,
              seats: seats,
              name: name,
              email: email,
              phone: phone,
              payment_method: selectedMethod,
              simulate_failure: simulateFailure
            })
          });

          const resData = await response.json();
          if (processingModal) processingModal.hide();

          if (resData.success) {
            window.location.href = resData.redirect_url;
          } else {
            if (paymentAlert) {
              paymentAlert.textContent = resData.message || 'Payment processing failed. Please try again.';
              paymentAlert.classList.remove('d-none');
              paymentAlert.scrollIntoView({ behavior: 'smooth' });
            }
          }
        } catch (err) {
          if (processingModal) processingModal.hide();
          if (paymentAlert) {
            paymentAlert.textContent = 'Network communication error. Please try again.';
            paymentAlert.classList.remove('d-none');
          }
        }
      }, 1200);
    });
  }
});
