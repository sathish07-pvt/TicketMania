/**
 * Ticket Mania - Main Client Application Logic
 * City Discovery, Geolocation, Interactive Fee Calculator Widget
 */

document.addEventListener('DOMContentLoaded', () => {
  initGeolocation();
  initFeeCalculator();
  initCityFilter();
});

/**
 * Browser Geolocation Support with Fallback
 */
function initGeolocation() {
  const detectBtn = document.getElementById('detectLocationBtn');
  if (!detectBtn) return;

  detectBtn.addEventListener('click', () => {
    if (!navigator.geolocation) {
      showToast('Geolocation is not supported by your browser.', 'warning');
      return;
    }

    const originalText = detectBtn.innerHTML;
    detectBtn.disabled = true;
    detectBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Locating nearest city...';

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const res = await fetch('/api/detect-city', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            })
          });

          const data = await res.json();
          if (data.success) {
            showToast(`Nearest city found: ${data.city_name} (${data.distance_km} km away)`, 'success');
            setTimeout(() => {
              window.location.reload();
            }, 800);
          } else {
            showToast(data.message || 'Could not find nearby city. Retaining Trichy.', 'info');
            detectBtn.disabled = false;
            detectBtn.innerHTML = originalText;
          }
        } catch (err) {
          console.error(err);
          showToast('Failed to contact location service. Retaining current city.', 'danger');
          detectBtn.disabled = false;
          detectBtn.innerHTML = originalText;
        }
      },
      (error) => {
        let msg = 'Location access was denied. Continuing with selected city.';
        if (error.code === error.TIMEOUT) msg = 'Location request timed out.';
        showToast(msg, 'info');
        detectBtn.disabled = false;
        detectBtn.innerHTML = originalText;
      },
      { timeout: 10000, enableHighAccuracy: false }
    );
  });
}

/**
 * Interactive Fee Calculator Widget
 * Formula: Base = 20 * N, Discount = 5 (odd) / 10 (even), Final = Base - Discount
 */
function initFeeCalculator() {
  const slider = document.getElementById('ticketSlider');
  if (!slider) return;

  const countDisplay = document.getElementById('calcTicketCount');
  const baseFeeDisplay = document.getElementById('calcBaseFee');
  const discountDisplay = document.getElementById('calcDiscount');
  const finalFeeDisplay = document.getElementById('calcFinalFee');
  const convFeeDisplay = document.getElementById('calcConventionalFee');
  const savingsDisplay = document.getElementById('calcSavings');
  const discountTypeBadge = document.getElementById('calcDiscountBadge');

  function updateCalculator() {
    const N = parseInt(slider.value, 10);
    const baseFee = 20 * N;
    const isOdd = (N % 2 !== 0);
    const discount = isOdd ? 5 : 10;
    const finalFee = baseFee - discount;
    const conventionalFee = 35 * N;
    const savings = conventionalFee - finalFee;

    if (countDisplay) countDisplay.textContent = N;
    if (baseFeeDisplay) baseFeeDisplay.textContent = `₹${baseFee}`;
    if (discountDisplay) discountDisplay.textContent = `-₹${discount}`;
    if (finalFeeDisplay) finalFeeDisplay.textContent = `₹${finalFee}`;
    if (convFeeDisplay) convFeeDisplay.textContent = `₹${conventionalFee}`;
    if (savingsDisplay) savingsDisplay.textContent = `₹${savings}`;

    if (discountTypeBadge) {
      discountTypeBadge.textContent = isOdd ? 'Odd Ticket: ₹5 Off' : 'Even Ticket: ₹10 Off!';
      discountTypeBadge.className = isOdd ? 'badge bg-warning text-dark' : 'badge bg-success';
    }
  }

  slider.addEventListener('input', updateCalculator);
  updateCalculator();
}

/**
 * Filter Cities in the City Modal Search
 */
function initCityFilter() {
  const searchInput = document.getElementById('cityModalSearch');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const cityItems = document.querySelectorAll('.city-grid-item');
    
    cityItems.forEach(item => {
      const cityName = item.getAttribute('data-city-name')?.toLowerCase() || '';
      if (cityName.includes(query)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  });
}

/**
 * UI Toast Helper
 */
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('tm-toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'tm-toast-container';
    toastContainer.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;max-width:360px;';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `alert alert-${type} shadow-lg alert-dismissible fade show mb-2`;
  toast.style.background = type === 'success' ? '#064e3b' : (type === 'danger' ? '#7f1d1d' : '#1e293b');
  toast.style.color = '#fff';
  toast.style.border = '1px solid rgba(255,255,255,0.15)';
  toast.innerHTML = `
    <div class="d-flex align-items-center justify-content-between">
      <span>${message}</span>
      <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="alert"></button>
    </div>
  `;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}
