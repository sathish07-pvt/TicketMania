/**
 * Ticket Mania - Interactive Seating Layout Controller
 * Dynamic seat selection, instant fee calculation, discount pill updates
 */

document.addEventListener('DOMContentLoaded', () => {
  const selectedSeats = new Map(); // seatNumber -> {seat_number, tier, price}
  const seats = document.querySelectorAll('.seat.available');
  const summaryDrawer = document.getElementById('summaryDrawer');
  const selectedSeatsBadges = document.getElementById('selectedSeatsBadges');
  const ticketCountDisplay = document.getElementById('drawerTicketCount');
  const subtotalDisplay = document.getElementById('drawerSubtotal');
  const baseFeeDisplay = document.getElementById('drawerBaseFee');
  const discountDisplay = document.getElementById('drawerDiscount');
  const finalFeeDisplay = document.getElementById('drawerFinalFee');
  const grandTotalDisplay = document.getElementById('drawerGrandTotal');
  const savingsDisplay = document.getElementById('drawerSavings');
  const discountBadge = document.getElementById('drawerDiscountBadge');
  const seatsDataInput = document.getElementById('seatsDataInput');
  const proceedBtn = document.getElementById('proceedCheckoutBtn');

  seats.forEach(seat => {
    seat.addEventListener('click', () => {
      const seatNumber = seat.getAttribute('data-seat-number');
      const tier = seat.getAttribute('data-tier');
      const price = parseFloat(seat.getAttribute('data-price'));

      if (selectedSeats.has(seatNumber)) {
        // Deselect
        selectedSeats.delete(seatNumber);
        seat.classList.remove('selected');
      } else {
        // Max 10 seats per booking
        if (selectedSeats.size >= 10) {
          alert('You can select a maximum of 10 seats per booking.');
          return;
        }
        // Select
        selectedSeats.set(seatNumber, { seat_number: seatNumber, tier, price });
        seat.classList.add('selected');
      }

      updatePricingUI();
    });
  });

  function updatePricingUI() {
    const seatList = Array.from(selectedSeats.values());
    const count = seatList.length;

    if (count === 0) {
      if (summaryDrawer) summaryDrawer.classList.remove('active');
      if (proceedBtn) proceedBtn.disabled = true;
      return;
    }

    if (summaryDrawer) summaryDrawer.classList.add('active');
    if (proceedBtn) proceedBtn.disabled = false;

    // Render badges
    if (selectedSeatsBadges) {
      selectedSeatsBadges.innerHTML = seatList
        .map(s => `<span class="selected-seats-badge">${s.seat_number} (₹${s.price})</span>`)
        .join('');
    }

    // Calculations
    const subtotal = seatList.reduce((acc, s) => acc + s.price, 0);
    const baseFee = 20 * count;
    const isOdd = (count % 2 !== 0);
    const discount = isOdd ? 5 : 10;
    const finalFee = Math.max(0, baseFee - discount);
    const grandTotal = subtotal + finalFee;
    const conventionalFee = 35 * count;
    const savings = Math.max(0, conventionalFee - finalFee);

    if (ticketCountDisplay) ticketCountDisplay.textContent = count;
    if (subtotalDisplay) subtotalDisplay.textContent = `₹${subtotal.toFixed(2)}`;
    if (baseFeeDisplay) baseFeeDisplay.textContent = `₹${baseFee.toFixed(2)}`;
    if (discountDisplay) discountDisplay.textContent = `-₹${discount.toFixed(2)}`;
    if (finalFeeDisplay) finalFeeDisplay.textContent = `₹${finalFee.toFixed(2)}`;
    if (grandTotalDisplay) grandTotalDisplay.textContent = `₹${grandTotal.toFixed(2)}`;
    if (savingsDisplay) savingsDisplay.textContent = `₹${savings.toFixed(2)}`;

    if (discountBadge) {
      discountBadge.textContent = isOdd ? '₹5 Ticket Mania Odd Discount' : '₹10 Ticket Mania Even Discount';
      discountBadge.className = isOdd ? 'convenience-fee-pill bg-warning text-dark' : 'convenience-fee-pill bg-success text-white';
    }

    if (seatsDataInput) {
      seatsDataInput.value = JSON.stringify(seatList);
    }
  }
});
