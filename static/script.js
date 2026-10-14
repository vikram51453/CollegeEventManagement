/* ============================================================
   College Event Management System – JavaScript
   Neutomni-Inspired Micro-Animations & Dynamic Interactions
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
  // ── 1. Real-time Live Clock in Utility Header ──
  function updateLiveClock() {
    const clockEl = document.getElementById('live-clock');
    if (!clockEl) return;
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    clockEl.textContent = timeStr;
  }
  updateLiveClock();
  setInterval(updateLiveClock, 1000);

  // ── 2. Sticky Navbar Scroll Polish ──
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', function () {
    if (window.scrollY > 20) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }
  }, { passive: true });

  // ── 3. Auto-close & Dismiss Flash Alerts with spring exit ──
  document.querySelectorAll('.alert-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const alert = this.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px) scale(0.96)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity .4s ease, transform .4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px) scale(0.96)';
      setTimeout(() => alert.remove(), 400);
    }, 6000);
  });

  // ── 4. Mobile Nav Toggle with smooth stagger ──
  const toggle = document.getElementById('nav-toggle');
  const navLinks = document.getElementById('nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // ── 5. Capacity Bars Smooth Fill ──
  document.querySelectorAll('.capacity-bar-fill').forEach(function (bar) {
    const target = bar.getAttribute('data-width') || '0';
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target + '%'; }, 250);
  });

  // ── 6. Intersection Observer with Blur Reveal & Stagger ──
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry, idx) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('is-visible');
        }, idx * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.observe-fade').forEach(function (el) {
    observer.observe(el);
  });

  // ── 7. Active Nav Link Detection ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function (a) {
    if (a.getAttribute('href') === currentPath) {
      a.classList.add('active');
    }
  });

  // ── 8. Live Form Email Validation ──
  const emailInput = document.getElementById('email');
  if (emailInput) {
    emailInput.addEventListener('input', function () {
      const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
      this.style.borderColor = this.value.length === 0
        ? 'var(--border-card)'
        : valid ? '#10b981' : 'var(--red-accent)';
    });
  }

  // ── 9. Confirmation on Destructive Actions ──
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(this.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // ── 10. Auto-uppercase Registration ID in tracking ──
  const regIdInput = document.getElementById('reg_id');
  if (regIdInput) {
    regIdInput.addEventListener('input', function () {
      const pos = this.selectionStart;
      this.value = this.value.toUpperCase();
      this.setSelectionRange(pos, pos);
    });
  }

  // ── 11. Tabular Numeric Counter Animation ──
  document.querySelectorAll('.stat-number[data-count], .stat-num[data-count]').forEach(function (el) {
    const target = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const duration = 1400;
    const startTime = performance.now();

    function updateCount(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutExpo
      const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      current = Math.round(ease * target);
      el.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(updateCount);
      }
    }
    requestAnimationFrame(updateCount);
  });

  // ── 12. Fluid 3D Micro-Tilt & Magnetic Parallax on Cards ──
  const interactiveCards = document.querySelectorAll('.event-card, .process-card, .hero-showcase');
  interactiveCards.forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const tiltX = (y / rect.height) * -6;
      const tiltY = (x / rect.width) * 6;
      card.style.transform = `perspective(900px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) translateY(-5px)`;
    });
    card.addEventListener('mouseleave', function () {
      card.style.transform = '';
    });
  });

  // ── 13. Magnetic Button Micro-Movement on Primary CTAs ──
  document.querySelectorAll('.btn-primary').forEach(function (btn) {
    btn.addEventListener('mousemove', function (e) {
      const rect = btn.getBoundingClientRect();
      const x = (e.clientX - rect.left - rect.width / 2) * 0.18;
      const y = (e.clientY - rect.top - rect.height / 2) * 0.18;
      btn.style.transform = `translate(${x}px, ${y}px) scale(1.02)`;
    });
    btn.addEventListener('mouseleave', function () {
      btn.style.transform = '';
    });
  });
});

// ── Copy registration ID to clipboard with toast notification ──
function copyRegId(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(function () {
      showToast('Registration ID copied to clipboard');
    });
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('Registration ID copied to clipboard');
  }
}

// ── Clean White & Red Toast Notification ──
function showToast(message) {
  const existing = document.getElementById('neutomni-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'neutomni-toast';
  toast.innerHTML = `<span style="color:#cf1830;margin-right:8px;font-weight:bold;">✔</span> ${message}`;
  Object.assign(toast.style, {
    position: 'fixed',
    bottom: '28px',
    right: '28px',
    zIndex: '99999',
    background: '#ffffff',
    color: '#0d0d12',
    padding: '14px 24px',
    borderRadius: '6px',
    border: '1px solid #e0e0e8',
    borderLeft: '4px solid #cf1830',
    boxShadow: '0 16px 36px rgba(207,24,48,0.18), 0 4px 12px rgba(0,0,0,0.06)',
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '0.82rem',
    fontWeight: '600',
    letterSpacing: '0.03em',
    opacity: '0',
    transform: 'translateY(12px) scale(0.96)',
    transition: 'opacity 0.35s cubic-bezier(0.16,1,0.3,1), transform 0.35s cubic-bezier(0.16,1,0.3,1)'
  });
  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0) scale(1)';
  });
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px) scale(0.96)';
    setTimeout(() => toast.remove(), 350);
  }, 2600);
}
