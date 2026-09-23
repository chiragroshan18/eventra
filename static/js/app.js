/**
 * EVENTRA - FRONTEND APPLICATION JAVASCRIPT
 * Modern Event Discovery & Ticket Booking Platform
 * Reusable functions, Fetch API communication, real-time UI updates
 */

// ==============================================================================
// REUSABLE HELPER FUNCTIONS (Frontend)
// ==============================================================================

/**
 * Perform Fetch API request with error handling and JSON parsing
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(endpoint, options);
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || `Request failed with status ${response.status}`);
    }

    return result;
  } catch (err) {
    console.error(`[API Error] ${method} ${endpoint}:`, err);
    throw err;
  }
}

/**
 * Display a modern toast notification
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/**
 * Format date string into readable format (e.g., Oct 15, 2026)
 */
function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Extract Month (e.g. OCT) and Day (e.g. 15) for date badge
 */
function getDateParts(dateStr) {
  if (!dateStr) return { month: 'NOV', day: '01' };
  const d = new Date(dateStr);
  const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
  return {
    month: months[d.getMonth()] || 'OCT',
    day: String(d.getDate()).padStart(2, '0')
  };
}

/**
 * Calculate total pricing
 */
function calculateTotal(unitPrice, quantity, fee = 5.00) {
  const p = parseFloat(unitPrice) || 0;
  const q = parseInt(quantity) || 1;
  const f = parseFloat(fee) || 0;
  const subtotal = p * q;
  const total = subtotal + f;
  return {
    unitPrice: p.toFixed(2),
    quantity: q,
    subtotal: subtotal.toFixed(2),
    bookingFee: f.toFixed(2),
    total: total.toFixed(2)
  };
}

/**
 * Validate customer booking form fields
 */
function validateForm(name, email, mobile, quantity, available) {
  if (!name || name.trim().length < 2) {
    return { valid: false, message: 'Please enter your full name (at least 2 letters).' };
  }

  const emailRegex = /^[^@]+@[^@]+\.[^@]+$/;
  if (!email || !emailRegex.test(email.trim())) {
    return { valid: false, message: 'Please enter a valid email address.' };
  }

  const mobileRegex = /^\+?[0-9\s\-]{7,15}$/;
  if (!mobile || !mobileRegex.test(mobile.trim())) {
    return { valid: false, message: 'Please enter a valid mobile number (7-15 digits).' };
  }

  const qty = parseInt(quantity);
  if (isNaN(qty) || qty <= 0) {
    return { valid: false, message: 'Please select a ticket quantity of at least 1.' };
  }

  if (qty > available) {
    return { valid: false, message: `Selected quantity (${qty}) exceeds available tickets (${available}).` };
  }

  return { valid: true };
}

/**
 * Render Event Cards into a grid container
 */
function renderEvents(eventsList, targetElement) {
  if (!targetElement) return;

  if (!eventsList || eventsList.length === 0) {
    targetElement.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">🎟️</div>
        <div class="empty-title">No Events Found</div>
        <div class="empty-desc">We couldn't find any events matching your criteria. Try adjusting your search query or filters.</div>
      </div>
    `;
    return;
  }

  targetElement.innerHTML = eventsList.map(event => {
    const dateParts = getDateParts(event.date);
    // Get minimum starting price across ticket types
    const prices = Object.values(event.ticket_types).map(t => t.price);
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;

    return `
      <div class="event-card" data-id="${event.id}">
        <div class="event-poster-wrapper">
          <img src="${event.image}" alt="${event.name}" class="event-poster" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80'" />
          <span class="category-tag">${event.category}</span>
          <div class="date-badge">
            <div class="date-badge-day">${dateParts.day}</div>
            <div class="date-badge-month">${dateParts.month}</div>
          </div>
        </div>
        <div class="event-content">
          <h3 class="event-title">${event.name}</h3>
          <div class="event-meta">
            <div class="meta-item">
              <span>📍</span> <span>${event.venue}, ${event.city}</span>
            </div>
            <div class="meta-item">
              <span>⏰</span> <span>${event.time}</span>
            </div>
          </div>
          <div class="event-footer">
            <div class="price-display">
              <span class="price-label">Starts at</span>
              <span class="price-val">$${minPrice.toFixed(2)}</span>
            </div>
            <a href="/events/${event.id}" class="btn-card-action">Book Now</a>
          </div>
        </div>
      </div>
    `;
  }).join('');
}


// ==============================================================================
// PAGE LOGIC CONTROLLERS
// ==============================================================================

/**
 * Controller for Homepage (index.html)
 */
async function initHomePage() {
  const featuredGrid = document.getElementById('featured-events-grid');
  const allEventsGrid = document.getElementById('all-events-grid');
  const searchInput = document.getElementById('home-search-input');
  const searchBtn = document.getElementById('home-search-btn');
  const categoryChips = document.querySelectorAll('.chip-item');

  try {
    const response = await apiRequest('/api/events');
    const events = response.data;

    if (featuredGrid) {
      const featured = events.filter(e => e.featured);
      renderEvents(featured.length > 0 ? featured : events.slice(0, 3), featuredGrid);
    }

    if (allEventsGrid) {
      renderEvents(events, allEventsGrid);
    }

    // Category filter click handler
    if (categoryChips) {
      categoryChips.forEach(chip => {
        chip.addEventListener('click', async () => {
          categoryChips.forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          const cat = chip.dataset.category;

          if (cat === 'all') {
            renderEvents(events, allEventsGrid || featuredGrid);
          } else {
            const filtered = events.filter(e => e.category.toLowerCase() === cat.toLowerCase());
            renderEvents(filtered, allEventsGrid || featuredGrid);
          }
        });
      });
    }

    // Search button click handler
    if (searchBtn && searchInput) {
      const handleSearch = async () => {
        const q = searchInput.value.trim();
        if (!q) {
          renderEvents(events, allEventsGrid || featuredGrid);
          return;
        }
        const searchRes = await apiRequest(`/api/events/search?q=${encodeURIComponent(q)}`);
        renderEvents(searchRes.data, allEventsGrid || featuredGrid);
      };

      searchBtn.addEventListener('click', handleSearch);
      searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
      });
    }

  } catch (err) {
    showToast('Failed to load events. Please refresh page.', 'error');
  }
}

/**
 * Controller for Events Catalog Page (events.html)
 */
async function initEventsPage() {
  const grid = document.getElementById('catalog-events-grid');
  const searchInput = document.getElementById('catalog-search-input');
  const categorySelect = document.getElementById('catalog-category-select');
  const dateInput = document.getElementById('catalog-date-input');
  const priceInput = document.getElementById('catalog-price-input');
  const priceValDisplay = document.getElementById('price-val-display');
  const availCheckbox = document.getElementById('catalog-avail-checkbox');
  const filterResetBtn = document.getElementById('filter-reset-btn');

  const fetchAndRenderFiltered = async () => {
    try {
      const q = searchInput ? searchInput.value.trim() : '';
      const cat = categorySelect ? categorySelect.value : '';
      const dt = dateInput ? dateInput.value : '';
      const maxP = priceInput ? priceInput.value : '';
      const avail = availCheckbox ? availCheckbox.checked : false;

      let url = `/api/events/search?q=${encodeURIComponent(q)}&category=${encodeURIComponent(cat)}&date=${dt}&max_price=${maxP}&available_only=${avail}`;
      const response = await apiRequest(url);
      renderEvents(response.data, grid);
    } catch (err) {
      showToast('Error filtering events.', 'error');
    }
  };

  // Attach event listeners for real-time reactive filtering
  if (searchInput) searchInput.addEventListener('input', fetchAndRenderFiltered);
  if (categorySelect) categorySelect.addEventListener('change', fetchAndRenderFiltered);
  if (dateInput) dateInput.addEventListener('change', fetchAndRenderFiltered);
  if (priceInput) {
    priceInput.addEventListener('input', () => {
      if (priceValDisplay) priceValDisplay.textContent = `$${priceInput.value}`;
      fetchAndRenderFiltered();
    });
  }
  if (availCheckbox) availCheckbox.addEventListener('change', fetchAndRenderFiltered);

  if (filterResetBtn) {
    filterResetBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (categorySelect) categorySelect.value = 'all';
      if (dateInput) dateInput.value = '';
      if (priceInput) {
        priceInput.value = priceInput.max;
        if (priceValDisplay) priceValDisplay.textContent = `$${priceInput.max}`;
      }
      if (availCheckbox) availCheckbox.checked = false;
      fetchAndRenderFiltered();
    });
  }

  // Initial fetch
  fetchAndRenderFiltered();
}

/**
 * Controller for Event Details Page (event-details.html)
 */
async function initEventDetailsPage(eventId) {
  const container = document.getElementById('event-detail-container');
  if (!container) return;

  try {
    const res = await apiRequest(`/api/events/${eventId}`);
    const event = res.data;

    let selectedType = 'General';
    let selectedQty = 1;
    const bookingFee = event.booking_fee || 5.00;

    // Render Event Details HTML Structure
    const dateFormatted = formatDate(event.date);
    const ticketTypesHtml = Object.keys(event.ticket_types).map(typeKey => {
      const info = event.ticket_types[typeKey];
      const isSelected = typeKey === selectedType;
      const isSoldOut = info.available <= 0;

      return `
        <div class="ticket-option-card ${isSelected ? 'selected' : ''} ${isSoldOut ? 'disabled' : ''}" data-type="${typeKey}">
          <div class="ticket-option-left">
            <span class="ticket-option-name">${typeKey} Ticket</span>
            <span class="ticket-option-avail">${isSoldOut ? 'SOLD OUT' : `${info.available} remaining`}</span>
          </div>
          <span class="ticket-option-price">$${info.price.toFixed(2)}</span>
        </div>
      `;
    }).join('');

    container.innerHTML = `
      <div class="event-details-layout">
        <!-- Left Column: Event Overview -->
        <div>
          <img src="${event.image}" alt="${event.name}" class="event-hero-poster" />
          <div class="detail-header-block">
            <span class="category-tag" style="position:static; display:inline-block; margin-bottom:0.75rem;">${event.category}</span>
            <h1 class="detail-title">${event.name}</h1>
          </div>

          <div class="detail-meta-grid">
            <div class="detail-meta-card">
              <div class="detail-meta-icon">📅</div>
              <div>
                <div class="detail-meta-label">Date & Time</div>
                <div class="detail-meta-value">${dateFormatted} at ${event.time}</div>
              </div>
            </div>
            <div class="detail-meta-card">
              <div class="detail-meta-icon">📍</div>
              <div>
                <div class="detail-meta-label">Location</div>
                <div class="detail-meta-value">${event.venue}, ${event.city}</div>
              </div>
            </div>
          </div>

          <h3 style="margin-bottom: 0.75rem; font-size: 1.3rem;">About This Event</h3>
          <p class="detail-description">${event.description}</p>
        </div>

        <!-- Right Column: Ticket Booking Panel -->
        <div>
          <div class="booking-card">
            <h3 class="booking-card-title">Select Tickets</h3>
            
            <div class="ticket-type-selector" id="ticket-type-selector">
              ${ticketTypesHtml}
            </div>

            <div class="quantity-control-group">
              <span class="form-label" style="margin:0;">Quantity</span>
              <div class="qty-counter">
                <button type="button" class="btn-qty" id="btn-qty-minus">-</button>
                <span class="qty-display" id="qty-val">${selectedQty}</span>
                <button type="button" class="btn-qty" id="btn-qty-plus">+</button>
              </div>
            </div>

            <!-- Price Breakdown Preview -->
            <div class="price-breakdown">
              <div class="breakdown-row">
                <span>Unit Price</span>
                <span id="summary-unit-price">$${event.ticket_types[selectedType].price.toFixed(2)}</span>
              </div>
              <div class="breakdown-row">
                <span>Quantity</span>
                <span id="summary-qty">${selectedQty}</span>
              </div>
              <div class="breakdown-row">
                <span>Subtotal</span>
                <span id="summary-subtotal">$${(event.ticket_types[selectedType].price * selectedQty).toFixed(2)}</span>
              </div>
              <div class="breakdown-row">
                <span>Booking Fee</span>
                <span>$${bookingFee.toFixed(2)}</span>
              </div>
              <div class="breakdown-row total">
                <span>Total</span>
                <span id="summary-total" style="color:var(--accent-amber);">$${(event.ticket_types[selectedType].price * selectedQty + bookingFee).toFixed(2)}</span>
              </div>
            </div>

            <!-- Customer Booking Form -->
            <form id="booking-form">
              <div class="form-group">
                <label class="form-label" for="cust-name">Full Name *</label>
                <input type="text" id="cust-name" class="form-input" placeholder="e.g. Alex Morgan" required />
              </div>

              <div class="form-group">
                <label class="form-label" for="cust-email">Email Address *</label>
                <input type="email" id="cust-email" class="form-input" placeholder="alex@example.com" required />
              </div>

              <div class="form-group">
                <label class="form-label" for="cust-mobile">Mobile Number *</label>
                <input type="tel" id="cust-mobile" class="form-input" placeholder="+1 555-0199" required />
              </div>

              <button type="submit" class="btn-submit-booking" id="btn-submit-booking">Confirm Booking</button>
            </form>
          </div>
        </div>
      </div>
    `;

    // Dynamic price recalculation function
    const updateCalculations = () => {
      const typeInfo = event.ticket_types[selectedType];
      const totals = calculateTotal(typeInfo.price, selectedQty, bookingFee);
      
      document.getElementById('summary-unit-price').textContent = `$${totals.unitPrice}`;
      document.getElementById('summary-qty').textContent = totals.quantity;
      document.getElementById('summary-subtotal').textContent = `$${totals.subtotal}`;
      document.getElementById('summary-total').textContent = `$${totals.total}`;

      const submitBtn = document.getElementById('btn-submit-booking');
      if (typeInfo.available <= 0) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sold Out';
      } else {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Confirm Booking';
      }
    };

    // Ticket type card selection handlers
    const typeCards = container.querySelectorAll('.ticket-option-card');
    typeCards.forEach(card => {
      card.addEventListener('click', () => {
        const typeKey = card.dataset.type;
        const info = event.ticket_types[typeKey];
        if (info.available <= 0) {
          showToast('Selected ticket type is sold out.', 'error');
          return;
        }

        typeCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedType = typeKey;
        
        // Reset qty if current qty exceeds available
        if (selectedQty > info.available) {
          selectedQty = info.available;
          document.getElementById('qty-val').textContent = selectedQty;
        }

        updateCalculations();
      });
    });

    // Quantity buttons handler
    const btnMinus = document.getElementById('btn-qty-minus');
    const btnPlus = document.getElementById('btn-qty-plus');
    const qtyDisplay = document.getElementById('qty-val');

    btnMinus.addEventListener('click', () => {
      if (selectedQty > 1) {
        selectedQty--;
        qtyDisplay.textContent = selectedQty;
        updateCalculations();
      }
    });

    btnPlus.addEventListener('click', () => {
      const available = event.ticket_types[selectedType].available;
      if (selectedQty < available) {
        selectedQty++;
        qtyDisplay.textContent = selectedQty;
        updateCalculations();
      } else {
        showToast(`Cannot select more than ${available} available tickets.`, 'info');
      }
    });

    // Form submission handler
    const form = document.getElementById('booking-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const name = document.getElementById('cust-name').value.trim();
      const email = document.getElementById('cust-email').value.trim();
      const mobile = document.getElementById('cust-mobile').value.trim();
      const available = event.ticket_types[selectedType].available;

      const val = validateForm(name, email, mobile, selectedQty, available);
      if (!val.valid) {
        showToast(val.message, 'error');
        return;
      }

      const submitBtn = document.getElementById('btn-submit-booking');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing Booking...';

      try {
        const payload = {
          name,
          email,
          mobile,
          event_id: event.id,
          ticket_type: selectedType,
          quantity: selectedQty
        };

        const res = await apiRequest('/api/bookings', 'POST', payload);
        const booking = res.data;
        showToast('Booking successfully created!', 'success');

        // Redirect to Digital Ticket View
        setTimeout(() => {
          window.location.href = `/ticket/${booking.booking_id}`;
        }, 800);

      } catch (err) {
        showToast(err.message || 'Failed to place booking.', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Confirm Booking';
      }
    });

  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⚠️</div>
        <div class="empty-title">Event Not Found</div>
        <div class="empty-desc">The requested event could not be found or has been removed.</div>
        <a href="/events" class="btn-card-action" style="margin-top:1rem; display:inline-block;">Browse All Events</a>
      </div>
    `;
  }
}

/**
 * Controller for Digital Ticket Page (ticket.html)
 */
async function initDigitalTicketPage(bookingId) {
  const container = document.getElementById('digital-ticket-container');
  if (!container) return;

  try {
    const res = await apiRequest(`/api/bookings/${bookingId}`);
    const b = res.data;

    const dateFormatted = formatDate(b.event_date);
    const statusClass = b.status.toLowerCase();

    container.innerHTML = `
      <div class="ticket-wrapper">
        <div class="ticket-stub">
          <div class="ticket-header">
            <div class="ticket-brand">
              <span style="color:var(--accent-pink);">✦</span> EVENTRA DIGITAL TICKET
            </div>
            <span class="ticket-status-badge ${statusClass}">${b.status}</span>
          </div>

          <div class="ticket-body">
            <div class="ticket-info-grid">
              <div style="grid-column: 1 / -1;">
                <div class="ticket-field-label">Event</div>
                <div class="ticket-field-val" style="font-size:1.3rem;">${b.event_name}</div>
              </div>

              <div>
                <div class="ticket-field-label">Booking ID</div>
                <div class="ticket-id-highlight">${b.booking_id}</div>
              </div>

              <div>
                <div class="ticket-field-label">Passenger / Guest</div>
                <div class="ticket-field-val">${b.customer.name}</div>
              </div>

              <div>
                <div class="ticket-field-label">Date & Time</div>
                <div class="ticket-field-val">${dateFormatted} at ${b.event_time}</div>
              </div>

              <div>
                <div class="ticket-field-label">Venue</div>
                <div class="ticket-field-val">${b.event_venue}, ${b.event_city}</div>
              </div>

              <div>
                <div class="ticket-field-label">Ticket Details</div>
                <div class="ticket-field-val">${b.quantity}x ${b.ticket_type} Ticket</div>
              </div>

              <div>
                <div class="ticket-field-label">Total Booking Value</div>
                <div class="ticket-field-val" style="color:var(--accent-amber);">$${b.pricing.total.toFixed(2)}</div>
              </div>
            </div>

            <div class="qr-container">
              <div class="qr-visual-matrix"></div>
              <div class="qr-caption">Scan for entry</div>
              <div style="font-size:0.65rem; color:#666; margin-top:0.2rem;">${b.booking_id}</div>
            </div>
          </div>

          <div class="ticket-actions-bar">
            <button onclick="window.print()" class="btn-secondary">🖨️ Print / Download Ticket</button>
            <a href="/bookings" class="btn-card-action">View All Bookings</a>
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🎟️</div>
        <div class="empty-title">Digital Ticket Not Found</div>
        <div class="empty-desc">We couldn't locate a ticket matching ID "${bookingId}".</div>
        <a href="/bookings" class="btn-card-action" style="margin-top:1rem; display:inline-block;">Go to My Bookings</a>
      </div>
    `;
  }
}

/**
 * Controller for My Bookings Dashboard (bookings.html)
 */
async function initBookingsPage() {
  const listContainer = document.getElementById('bookings-list-container');
  const totalCountEl = document.getElementById('metric-total');
  const confirmedCountEl = document.getElementById('metric-confirmed');
  const cancelledCountEl = document.getElementById('metric-cancelled');
  const ticketsCountEl = document.getElementById('metric-tickets');
  const valueEl = document.getElementById('metric-value');
  const searchInput = document.getElementById('dashboard-search-input');
  const statusChips = document.querySelectorAll('[data-booking-status]');

  let allBookings = [];
  let currentStatus = 'all';
  let searchQuery = '';

  const renderDashboard = () => {
    // 1. Calculate Metrics on full dataset
    const total = allBookings.length;
    const confirmedList = allBookings.filter(b => b.status === 'Confirmed');
    const confirmedCount = confirmedList.length;
    const cancelledCount = allBookings.filter(b => b.status === 'Cancelled').length;
    
    const totalTickets = confirmedList.reduce((sum, b) => sum + (b.quantity || 0), 0);
    const totalValue = confirmedList.reduce((sum, b) => sum + (b.pricing ? b.pricing.total : 0), 0);

    if (totalCountEl) totalCountEl.textContent = total;
    if (confirmedCountEl) confirmedCountEl.textContent = confirmedCount;
    if (cancelledCountEl) cancelledCountEl.textContent = cancelledCount;
    if (ticketsCountEl) ticketsCountEl.textContent = totalTickets;
    if (valueEl) valueEl.textContent = `$${totalValue.toFixed(2)}`;

    if (!listContainer) return;

    // 2. Filter bookings list
    let filtered = allBookings;

    if (currentStatus !== 'all') {
      filtered = filtered.filter(b => b.status.toLowerCase() === currentStatus.toLowerCase());
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(b => 
        b.booking_id.toLowerCase().includes(q) ||
        b.event_name.toLowerCase().includes(q) ||
        b.event_venue.toLowerCase().includes(q) ||
        (b.customer && b.customer.name.toLowerCase().includes(q))
      );
    }

    if (filtered.length === 0) {
      listContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🎟️</div>
          <div class="empty-title">No Matching Reservations</div>
          <div class="empty-desc">No reservations match your current filter or search criteria.</div>
          <a href="/events" class="btn-card-action" style="margin-top:1rem; display:inline-block;">Explore Events</a>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = filtered.map(b => {
      const isConfirmed = b.status === 'Confirmed';
      const dateStr = formatDate(b.event_date);

      return `
        <div class="booking-item-card" data-id="${b.booking_id}">
          <div class="booking-item-main">
            <img src="${b.event_image || 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80'}" alt="${b.event_name}" class="booking-item-poster" />
            <div class="booking-item-info">
              <div style="display:flex; align-items:center; gap:0.5rem;">
                <span class="ticket-id-highlight" style="font-size:0.85rem;">${b.booking_id}</span>
                <span class="ticket-status-badge ${b.status.toLowerCase()}">${b.status}</span>
              </div>
              <h3 class="booking-item-title">${b.event_name}</h3>
              <div class="booking-item-sub">
                <span>👤 ${b.customer ? b.customer.name : 'Guest'}</span>
                <span>📅 ${dateStr} at ${b.event_time}</span>
                <span>📍 ${b.event_venue}</span>
                <span>🎟️ ${b.quantity}x ${b.ticket_type} ($${b.pricing.total.toFixed(2)})</span>
              </div>
            </div>
          </div>

          <div class="booking-item-actions">
            <a href="/ticket/${b.booking_id}" class="btn-secondary">View Ticket</a>
            ${isConfirmed ? `
              <button type="button" class="btn-danger btn-cancel-booking" data-id="${b.booking_id}">Cancel</button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');

    // Attach cancel button event handlers
    const cancelBtns = listContainer.querySelectorAll('.btn-cancel-booking');
    cancelBtns.forEach(btn => {
      btn.addEventListener('click', async () => {
        const bId = btn.dataset.id;
        if (!confirm(`Are you sure you want to cancel booking ${bId}? This will release your tickets back to available stock.`)) {
          return;
        }

        try {
          btn.disabled = true;
          btn.textContent = 'Cancelling...';

          await apiRequest(`/api/bookings/${bId}/cancel`, 'PATCH');
          showToast(`Booking ${bId} cancelled successfully.`, 'success');
          fetchAndRenderBookings(); // Refresh live state
        } catch (err) {
          showToast(err.message || 'Failed to cancel booking.', 'error');
          btn.disabled = false;
          btn.textContent = 'Cancel';
        }
      });
    });
  };

  const fetchAndRenderBookings = async () => {
    try {
      const res = await apiRequest('/api/bookings');
      allBookings = res.data || [];
      renderDashboard();
    } catch (err) {
      if (listContainer) {
        listContainer.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">⚠️</div>
            <div class="empty-title">Failed to load bookings</div>
            <div class="empty-desc">Could not connect to server. Please try again.</div>
          </div>
        `;
      }
    }
  };

  // Event handlers for status chips
  statusChips.forEach(chip => {
    chip.addEventListener('click', () => {
      statusChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentStatus = chip.dataset.bookingStatus || 'all';
      renderDashboard();
    });
  });

  // Event handler for search input
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim();
      renderDashboard();
    });
  }

  fetchAndRenderBookings();
}
