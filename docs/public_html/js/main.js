/**
 * ImpressionCore Genesis Web Platform — Master Interaction & Navigation Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initStatsCounters();
  initImageModals();
  initActiveLinks();
});

/* ── Navigation & Header Controls ── */
function initNavigation() {
  const header = document.querySelector('.ic-header');
  const mobileToggle = document.querySelector('.ic-mobile-toggle');
  const nav = document.querySelector('.ic-nav');

  // Scroll Header Effect
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      header.style.background = 'rgba(4, 6, 10, 0.95)';
      header.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.6)';
    } else {
      header.style.background = 'rgba(4, 6, 10, 0.85)';
      header.style.boxShadow = 'none';
    }
  });

  // Mobile Menu Toggle
  if (mobileToggle && nav) {
    mobileToggle.addEventListener('click', () => {
      const isVisible = nav.style.display === 'flex';
      nav.style.display = isVisible ? 'none' : 'flex';
      if (!isVisible) {
        nav.style.flexDirection = 'column';
        nav.style.position = 'absolute';
        nav.style.top = 'var(--header-height)';
        nav.style.left = '0';
        nav.style.width = '100%';
        nav.style.background = 'rgba(6, 9, 15, 0.98)';
        nav.style.padding = '2rem';
        nav.style.borderBottom = '1px solid var(--border-glass)';
      }
    });
  }
}

/* ── Highlight Active Navigation Link ── */
function initActiveLinks() {
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.ic-nav-link');

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

/* ── Animated Stats Counters ── */
function initStatsCounters() {
  const statElements = document.querySelectorAll('[data-counter]');
  if (!statElements.length) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseFloat(el.getAttribute('data-counter'));
        const suffix = el.getAttribute('data-suffix') || '';
        const decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
        let start = 0;
        const duration = 1500;
        const startTime = performance.now();

        function update(now) {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / duration, 1);
          // Ease out cubic
          const ease = 1 - Math.pow(1 - progress, 3);
          const current = start + (target - start) * ease;
          el.innerText = current.toFixed(decimals) + suffix;

          if (progress < 1) {
            requestAnimationFrame(update);
          } else {
            el.innerText = target.toFixed(decimals) + suffix;
          }
        }

        requestAnimationFrame(update);
        obs.unobserve(el);
      }
    });
  }, { threshold: 0.25 });

  statElements.forEach(el => observer.observe(el));
}

/* ── Modal Zoom for High-Res Illustration Figures ── */
function initImageModals() {
  const figures = document.querySelectorAll('.ic-figure-frame img');
  if (!figures.length) return;

  // Create Modal element in DOM
  const modal = document.createElement('div');
  modal.className = 'ic-img-modal';
  modal.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(4, 6, 10, 0.94); backdrop-filter: blur(20px);
    display: none; align-items: center; justify-content: center;
    z-index: 9999; cursor: zoom-out; padding: 2rem;
  `;
  
  const modalImg = document.createElement('img');
  modalImg.style.cssText = `
    max-width: 95%; max-height: 90vh; border-radius: 12px;
    border: 1.5px solid var(--accent-cyan); box-shadow: 0 0 40px rgba(0, 240, 255, 0.35);
  `;
  modal.appendChild(modalImg);
  document.body.appendChild(modal);

  figures.forEach(img => {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', () => {
      modalImg.src = img.src;
      modal.style.display = 'flex';
    });
  });

  modal.addEventListener('click', () => {
    modal.style.display = 'none';
  });
}
