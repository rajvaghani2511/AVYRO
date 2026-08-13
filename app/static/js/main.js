/**
 * AVYRO E-Commerce Core JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initSearchOverlay();
  initProductGallery();
  initQuantityControls();
  initAnnouncementRotator();
});

// Announcement Rotator
function initAnnouncementRotator() {
  const slides = document.querySelectorAll('.announcement-slide');
  if (slides.length <= 1) return;

  let currentIndex = 0;
  setInterval(() => {
    slides[currentIndex].classList.remove('active');
    currentIndex = (currentIndex + 1) % slides.length;
    slides[currentIndex].classList.add('active');
  }, 4000);
}

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
            resultsContainer.innerHTML = data.map(item => {
              const imgSrc = item.image_url || (item.image ? (item.image.startsWith('http') ? item.image : `/static/uploads/${item.image}`) : '/static/uploads/default-product.webp');
              const priceVal = typeof item.price === 'number' ? (Number.isInteger(item.price) ? `₹${item.price.toLocaleString('en-IN')}` : `₹${item.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}`) : item.price;
              
              return `
                <a href="/product/${item.slug}" class="search-result-item" onclick="closeSearchOverlay()">
                  <img src="${imgSrc}" class="search-result-img" alt="${item.name}" onerror="this.src='/static/uploads/default-product.webp'">
                  <div class="flex-grow-1 overflow-hidden">
                    <div class="fw-bold font-serif fs-6 text-dark text-truncate">${item.name}</div>
                    <div class="text-muted extra-small">${item.category || 'AVYRO Collection'}</div>
                  </div>
                  <div class="fw-bold text-primary font-serif">${priceVal}</div>
                </a>
              `;
            }).join('');
          }
        })
        .catch(err => console.error('Search error:', err));
    }, 250);
  });
}

// Product Gallery Main Image & Thumbnail Switcher
function initProductGallery() {
  const mainImg = document.getElementById('mainGalleryImage');
  const thumbs = document.querySelectorAll('.thumb-item');
  const prevBtn = document.getElementById('galleryPrevBtn');
  const nextBtn = document.getElementById('galleryNextBtn');

  if (!mainImg) return;

  let currentIndex = 0;
  const imagesList = [];

  if (thumbs.length > 0) {
    thumbs.forEach((thumb, idx) => {
      const src = thumb.getAttribute('data-src');
      if (src) imagesList.push(src);
      
      thumb.addEventListener('click', () => {
        switchImage(idx);
      });
    });
  } else if (mainImg.src) {
    imagesList.push(mainImg.src);
  }

  function switchImage(index) {
    if (imagesList.length === 0) return;
    
    // Looping index bounds
    if (index < 0) {
      currentIndex = imagesList.length - 1;
    } else if (index >= imagesList.length) {
      currentIndex = 0;
    } else {
      currentIndex = index;
    }

    const newSrc = imagesList[currentIndex];

    // Transition effect
    mainImg.style.opacity = '0.3';
    mainImg.style.transition = 'opacity 0.15s ease';

    setTimeout(() => {
      mainImg.src = newSrc;
      mainImg.style.opacity = '1';
    }, 150);

    // Synchronize active thumbnail highlight
    if (thumbs.length > 0) {
      thumbs.forEach((t, i) => {
        if (i === currentIndex) {
          t.classList.add('active');
          t.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        } else {
          t.classList.remove('active');
        }
      });
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      switchImage(currentIndex - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      switchImage(currentIndex + 1);
    });
  }
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

// Global Add to Cart Function with Fly-to-Cart Animation
function addToCart(productId, quantity = 1, btnElement = null) {
  let triggerElem = btnElement;
  if (!triggerElem && typeof window !== 'undefined' && window.event) {
    triggerElem = window.event.currentTarget || window.event.target;
  }

  // Trigger smooth curved fly-to-cart visual animation immediately
  try {
    triggerFlyToCartAnimation(triggerElem);
  } catch (err) {
    console.error('Fly-to-cart animation notice:', err);
  }

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

// Smooth & Premium Fly-To-Cart Curved Path Animation
function triggerFlyToCartAnimation(triggerElem) {
  const cartTarget = document.getElementById('navCartIconBtn') || 
                     document.querySelector('.cart-badge-count') || 
                     document.querySelector('a[href*="/cart"]');
  if (!cartTarget) return;

  // Locate the product image source element
  let imgElem = null;
  if (triggerElem && triggerElem.closest) {
    const container = triggerElem.closest('.product-card') || 
                      triggerElem.closest('.product-gallery-main') || 
                      triggerElem.closest('.row') || 
                      triggerElem.closest('tr');
    if (container) {
      imgElem = container.querySelector('.product-card-img-wrap img') || 
                container.querySelector('#mainGalleryImage') || 
                container.querySelector('.product-gallery-main img') || 
                container.querySelector('img');
    }
  }

  if (!imgElem) {
    imgElem = document.getElementById('mainGalleryImage') || 
              document.querySelector('.product-card-img-wrap img');
  }

  const targetRect = cartTarget.getBoundingClientRect();
  const targetX = targetRect.left + targetRect.width / 2;
  const targetY = targetRect.top + targetRect.height / 2;

  let startCenterX, startCenterY, startWidth, startHeight, flyerNode;

  if (imgElem && imgElem.offsetParent !== null && imgElem.getBoundingClientRect().width > 0) {
    const imgRect = imgElem.getBoundingClientRect();
    startWidth = imgRect.width;
    startHeight = imgRect.height;
    startCenterX = imgRect.left + startWidth / 2;
    startCenterY = imgRect.top + startHeight / 2;

    flyerNode = document.createElement('img');
    flyerNode.src = imgElem.currentSrc || imgElem.src;
    flyerNode.className = 'flying-cart-item';
    flyerNode.style.width = `${startWidth}px`;
    flyerNode.style.height = `${startHeight}px`;
  } else {
    // Fallback if no visible image is found
    const btnRect = (triggerElem && triggerElem.getBoundingClientRect) ? 
                    triggerElem.getBoundingClientRect() : 
                    { left: window.innerWidth / 2, top: window.innerHeight / 2, width: 40, height: 40 };
    startWidth = 50;
    startHeight = 50;
    startCenterX = btnRect.left + btnRect.width / 2;
    startCenterY = btnRect.top + btnRect.height / 2;

    flyerNode = document.createElement('div');
    flyerNode.className = 'flying-cart-item flying-cart-fallback';
    flyerNode.innerHTML = '<i class="bi bi-bag-fill"></i>';
    flyerNode.style.width = '50px';
    flyerNode.style.height = '50px';
  }

  // Set initial off-screen / zero origin positioning via CSS translate3d
  flyerNode.style.top = '0px';
  flyerNode.style.left = '0px';
  document.body.appendChild(flyerNode);

  // Control point for a smooth curved arc path (curves upward towards the navbar)
  const controlX = (startCenterX + targetX) / 2 - 40;
  const controlY = Math.min(startCenterY, targetY) - 90;

  const duration = 750; // ms
  const startTime = performance.now();

  function animate(currentTime) {
    const elapsed = currentTime - startTime;
    const t = Math.min(elapsed / duration, 1);

    // Easing: quadratic ease-out
    const easeT = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;

    // Quadratic Bezier interpolation
    const curX = (1 - easeT) * (1 - easeT) * startCenterX + 2 * (1 - easeT) * easeT * controlX + easeT * easeT * targetX;
    const curY = (1 - easeT) * (1 - easeT) * startCenterY + 2 * (1 - easeT) * easeT * controlY + easeT * easeT * targetY;

    // Scale down smoothly as it approaches cart
    const scale = 1 - 0.83 * easeT;
    // Fade out during the final 15% of flight path
    const opacity = t > 0.85 ? 1 - ((t - 0.85) / 0.15) : 1;
    const rotate = easeT * 12;

    flyerNode.style.transform = `translate3d(${curX - startWidth / 2}px, ${curY - startHeight / 2}px, 0) scale(${scale}) rotate(${rotate}deg)`;
    flyerNode.style.opacity = opacity;

    if (t < 1) {
      requestAnimationFrame(animate);
    } else {
      if (flyerNode.parentNode) {
        flyerNode.parentNode.removeChild(flyerNode);
      }
      bounceCartIcon(cartTarget);
    }
  }

  requestAnimationFrame(animate);
}

// Bounce / Pulse Cart Icon on Navbar
function bounceCartIcon(cartTarget) {
  if (!cartTarget) return;
  cartTarget.classList.remove('cart-bounce');
  void cartTarget.offsetWidth; // Force CSS repaint
  cartTarget.classList.add('cart-bounce');
  setTimeout(() => {
    cartTarget.classList.remove('cart-bounce');
  }, 600);
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
