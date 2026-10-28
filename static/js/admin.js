/**
 * Ticket Mania - Admin Dashboard Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initAdminCharts();
  initSeatEditor();
});

function initAdminCharts() {
  const chartCanvas = document.getElementById('revenueChart');
  if (!chartCanvas || typeof Chart === 'undefined') return;

  new Chart(chartCanvas, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          label: 'Revenue (₹)',
          data: [12400, 15600, 18900, 22100, 34500, 48200, 42100],
          borderColor: '#ff2a4b',
          backgroundColor: 'rgba(255, 42, 75, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.35
        },
        {
          label: 'Fee Savings Given (₹)',
          data: [1200, 1550, 1900, 2200, 3600, 5100, 4400],
          borderColor: '#00e676',
          backgroundColor: 'rgba(0, 230, 118, 0.08)',
          borderWidth: 2,
          fill: true,
          tension: 0.35
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#94a3b8' }
        }
      },
      scales: {
        x: {
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

function initSeatEditor() {
  const editorSeats = document.querySelectorAll('.admin-editor-seat');
  if (!editorSeats.length) return;

  editorSeats.forEach(seat => {
    seat.addEventListener('click', async () => {
      const showId = seat.getAttribute('data-show-id');
      const seatNumber = seat.getAttribute('data-seat-number');

      try {
        const res = await fetch('/admin/api/toggle-seat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ show_id: parseInt(showId, 10), seat_number: seatNumber })
        });
        const data = await res.json();
        if (data.success) {
          if (data.action === 'blocked') {
            seat.classList.remove('available');
            seat.classList.add('booked');
          } else {
            seat.classList.remove('booked');
            seat.classList.add('available');
          }
        }
      } catch (err) {
        console.error('Failed to toggle seat', err);
      }
    });
  });
}
