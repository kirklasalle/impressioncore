/**
 * ImpressionCore Genesis Web Platform — Master Interaction & Navigation Engine
 * World-Class Cyber-Noir Navigation, Magnetic Physics & Telemetry Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  initWorldClassNavigation();
  initTelemetryHUD();
  initKeyboardShortcuts();
  initStatsCounters();
  initImageModals();
});

/* ═══════════════════════════════════════════════════════════════════════════
   1. World-Class Navigation & Magnetic Physics Engine
   ═══════════════════════════════════════════════════════════════════════════ */
function initWorldClassNavigation() {
  const header = document.getElementById('icHeader');
  const navIsland = document.getElementById('icNavIsland');
  const slider = document.getElementById('icNavSlider');
  const navItems = document.querySelectorAll('.ic-nav-item');
  const mobileToggle = document.getElementById('icMobileToggle');
  const mobileDrawer = document.getElementById('icMobileDrawer');

  // Scroll Header Elevation Physics
  const handleScroll = () => {
    if (window.scrollY > 24) {
      header?.classList.add('scrolled');
    } else {
      header?.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // Determine Active Navigation Page
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  let activeNavType = 'genesis';
  if (currentPath === 'architecture.html' || currentPath === 'sensory.html') {
    activeNavType = 'architecture';
  } else if (currentPath === 'models.html') {
    activeNavType = 'models';
  } else if (currentPath === 'builder.html' || currentPath === 'agents-mcp.html') {
    activeNavType = 'studio';
  } else if (currentPath === 'docs.html' || currentPath === 'governance.html') {
    activeNavType = 'governance';
  }

  // Set active classes on top-level and drawer links
  let activeItemEl = null;
  navItems.forEach(item => {
    const link = item.querySelector('.ic-nav-link');
    if (link && link.getAttribute('data-nav') === activeNavType) {
      link.classList.add('active');
      activeItemEl = item;
    } else if (link) {
      link.classList.remove('active');
    }
  });

  document.querySelectorAll('.ic-drawer-link').forEach(link => {
    const href = link.getAttribute('href')?.split('#')[0];
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // Magnetic Nav Slider Position Helper
  function positionSlider(targetEl) {
    if (!slider || !navIsland || !targetEl) {
      if (slider) slider.style.opacity = '0';
      return;
    }
    const islandRect = navIsland.getBoundingClientRect();
    const targetRect = targetEl.getBoundingClientRect();

    const leftOffset = targetRect.left - islandRect.left;
    const width = targetRect.width;

    slider.style.opacity = '1';
    slider.style.transform = `translateX(${leftOffset}px)`;
    slider.style.width = `${width}px`;
  }

  // Initial Slider Placement
  if (activeItemEl) {
    setTimeout(() => positionSlider(activeItemEl), 100);
  }

  // Hover Magnetic Tracking
  navItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      positionSlider(item);
    });

    item.addEventListener('mouseleave', () => {
      if (activeItemEl) {
        positionSlider(activeItemEl);
      } else if (slider) {
        slider.style.opacity = '0';
      }
    });
  });

  window.addEventListener('resize', () => {
    if (activeItemEl) positionSlider(activeItemEl);
  });

  // Mobile Drawer Toggle & Body Scroll Lock
  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileDrawer.classList.contains('open');
      if (isOpen) {
        mobileDrawer.classList.remove('open');
        mobileToggle.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      } else {
        mobileDrawer.classList.add('open');
        mobileToggle.classList.add('open');
        mobileToggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
      }
    });

    // Close on link click
    mobileDrawer.querySelectorAll('.ic-drawer-link').forEach(link => {
      link.addEventListener('click', () => {
        mobileDrawer.classList.remove('open');
        mobileToggle.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }

  // Dropdown Keyboard Accessibility
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      navItems.forEach(item => item.classList.remove('open'));
      const hud = document.getElementById('icTelemetryHud');
      hud?.classList.remove('open');
      if (mobileDrawer?.classList.contains('open')) {
        mobileDrawer.classList.remove('open');
        mobileToggle?.classList.remove('open');
        document.body.style.overflow = '';
      }
    }
  });
}

/* ═══════════════════════════════════════════════════════════════════════════
   2. Live Hardware Telemetry HUD Engine
   ═══════════════════════════════════════════════════════════════════════════ */
function initTelemetryHUD() {
  const hudWrap = document.getElementById('icTelemetryHud');
  const capsule = hudWrap?.querySelector('.ic-telemetry-capsule');
  if (!hudWrap || !capsule) return;

  capsule.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = hudWrap.classList.toggle('open');
    capsule.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close HUD on click outside
  document.addEventListener('click', (e) => {
    if (!hudWrap.contains(e.target)) {
      hudWrap.classList.remove('open');
      capsule.setAttribute('aria-expanded', 'false');
    }
  });

  // Live Micro-Pulse Simulation for VRAM metric
  const valEl = capsule.querySelector('.ic-telemetry-val');
  if (valEl) {
    setInterval(() => {
      // Fluctuates slightly between 3.81 and 3.84 GB
      const base = 3.82;
      const jitter = (Math.random() * 0.04 - 0.02);
      const current = (base + jitter).toFixed(2);
      valEl.innerHTML = `${current}<span class="ic-telemetry-sub">/4GB</span>`;
    }, 3500);
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   3. Global Command Palette & Keyboard Shortcuts (⌘K / Ctrl+K)
   ═══════════════════════════════════════════════════════════════════════════ */
function initKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      // If already on docs page, focus search input
      const docSearchInput = document.getElementById('docSearchInput');
      if (docSearchInput) {
        docSearchInput.focus();
        docSearchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        // Navigate to docs search
        window.location.href = 'docs.html';
      }
    }
  });
}

/* ═══════════════════════════════════════════════════════════════════════════
   4. Animated Stats Counters
   ═══════════════════════════════════════════════════════════════════════════ */
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

/* ═══════════════════════════════════════════════════════════════════════════
   5. High-Resolution Modal Zoom Engine
   ═══════════════════════════════════════════════════════════════════════════ */
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
