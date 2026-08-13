/**
 * AVYRO E-Commerce Core JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initSearchOverlay();
  initProductGallery();
  initQuantityControls();
});

// Toast Notification System
function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'avyro-toast-container';
    document.body.appendChild(container);
  }

  const iconMap = {
    success: 'bi-check-circle-fill text-warning',
    danger: 'bi-exclamation-triangle-fill text-danger',
    warning: 'bi-exclamation-circle-fill text-warning',
    info: 'bi-info-circle-fill text-light'
  };

  const toast = document.createElement('div');
  toast.className = 'avyro-toast';
  toast.innerHTML = `
    <i class="bi ${iconMap[type] || iconMap.info} fs-5"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Navbar Scroll Effect
function initNavbarScroll() {
  const navbar = document.querySelector('.avyro-navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// Fullscreen Search Overlay Trigger
function openSearchOverlay() {
  const overlay = document.getElementById('searchOverlay');
  const input = document.getElementById('overlaySearchInput');
  if (overlay) {
    overlay.style.display = 'flex';
    if (input) {
      input.focus();
    }
  }
}

function closeSearchOverlay() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

function initSearchOverlay() {
  const input = document.getElementById('overlaySearchInput');
  const resultsContainer = document.getElementById('overlaySearchResults');
  if (!input || !resultsContainer) return;

  let debounceTimer;

  input.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();

    if (query.length < 2) {
      resultsContainer.innerHTML = `
        <div class="text-center py-4 text-muted small">
          Start typing to discover luxury products, apparel & accessories...
        </div>
      `;
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          if (data.length === 0) {
            resultsContainer.innerHTML = `
              <div class="p-4 text-center text-muted small">
                No matching products found for "${query}"
              </div>
            `;
          } else {
            resultsContainer.innerHTML = data.map(item => `
              <a href="/product/${item.slug}" class="search-result-item" onclick="closeSearchOverlay()">
                <img src="/static/uploads/${item.image}" class="search-result-img" alt="${item.name}" onerror="this.src='https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=100'">
                <div class="flex-grow-1 overflow-hidden">
                  <div class="fw-bold font-serif fs-6 text-dark text-truncate">${item.name}</div>
                  <div class="text-muted extra-small">${item.category || 'AVYRO Collection'}</div>
                </div>
                <div class="fw-bold text-primary font-serif">₹${item.price.toFixed(2)}</div>
              </a>
            `).join('');
          }
        })
        .catch(err => console.error('Search error:', err));
    }, 250);
  });
}

// Product Gallery Thumbnail Switcher
function initProductGallery() {
  const mainImg = document.getElementById('mainGalleryImage');
  const thumbs = document.querySelectorAll('.thumb-item');

  if (!mainImg || !thumbs.length) return;

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      const newSrc = thumb.getAttribute('data-src');
      if (newSrc) {
        mainImg.style.opacity = '0.4';
        setTimeout(() => {
          mainImg.src = newSrc;
          mainImg.style.opacity = '1';
        }, 150);
      }
    });
  });
}

// Quantity Inputs
function initQuantityControls() {
  document.querySelectorAll('.quantity-control').forEach(ctrl => {
    const btnMinus = ctrl.querySelector('.btn-qty-minus');
    const btnPlus = ctrl.querySelector('.btn-qty-plus');
    const input = ctrl.querySelector('.qty-input');

    if (!input) return;

    if (btnMinus) {
      btnMinus.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          input.dispatchEvent(new Event('change'));
        }
      });
    }

    if (btnPlus) {
      btnPlus.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        let max = parseInt(input.getAttribute('max')) || 99;
        if (val < max) {
          input.value = val + 1;
          input.dispatchEvent(new Event('change'));
        } else {
          showToast(`Maximum available stock reached (${max})`, 'warning');
        }
      });
    }
  });
}

// Global Add to Cart Function
function addToCart(productId, quantity = 1) {
  fetch('/api/cart/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, quantity: parseInt(quantity) })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      // Update Navbar Badges
      const badges = document.querySelectorAll('.cart-badge-count');
      badges.forEach(b => { b.innerText = data.cart_count; });
    } else {
      showToast(data.message || 'Error adding to cart', 'danger');
    }
  })
  .catch(err => {
    console.error(err);
    showToast('Failed to connect to server', 'danger');
  });
}

// Global Wishlist Toggle Function
function toggleWishlist(productId, btnElement) {
  fetch('/api/wishlist/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId })
  })
  .then(res => {
    if (res.status === 401) {
      window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
      return;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    if (data.success) {
      showToast(data.message, data.added ? 'success' : 'info');
      
      const heartIcon = btnElement.querySelector('i');
      if (data.added) {
        btnElement.classList.add('active');
        if (heartIcon) heartIcon.className = 'bi bi-heart-fill text-danger';
      } else {
        btnElement.classList.remove('active');
        if (heartIcon) heartIcon.className = 'bi bi-heart';
      }

      const wishlistBadges = document.querySelectorAll('.wishlist-badge-count');
      wishlistBadges.forEach(b => { b.innerText = data.wishlist_count; });
    } else {
      showToast(data.message, 'danger');
    }
  })
  .catch(err => console.error('Wishlist error:', err));
}
