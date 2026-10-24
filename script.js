/* Gaby Padilla Makeup Artist · Website navigation and booking. */
// AgendaPro live listing verified October 23, 2026; update URL here if Gaby changes it.
const BOOKING_URLS = {
  general: 'https://gabypadillamakeupartist.site.agendapro.com/mx/sucursal/578261',
  bridal: 'https://gabypadillamakeupartist.site.agendapro.com/mx/sucursal/578261', // No verified direct service deep link; opens the full listing.
  xv: 'https://gabypadillamakeupartist.site.agendapro.com/mx/sucursal/578261'      // No verified direct service deep link; opens the full listing.
};
document.querySelectorAll('[data-booking]').forEach(a => {
  const type = a.getAttribute('data-booking') || 'general';
  a.href = BOOKING_URLS[type] || BOOKING_URLS.general;
});
const toggle = document.getElementById('menu-toggle');
const menu = document.getElementById('mobile-menu');
const menuClose = document.getElementById('menu-close');
const backgroundRegions = document.querySelectorAll('main, footer, .topline, .header-inner, .mobile-booking-bar');
function setMenuOpen(open) {
  const hadFocus = menu.contains(document.activeElement);
  menu.hidden = !open;
  toggle.setAttribute('aria-expanded', String(open));
  document.documentElement.classList.toggle('menu-open', open);
  document.body.classList.toggle('menu-open', open);
  backgroundRegions.forEach(region => region.inert = open);
  if (open) menuClose.focus({ preventScroll: true });
  else if (hadFocus) toggle.focus({ preventScroll: true });
}
toggle.addEventListener('click', () => setMenuOpen(menu.hidden));
menuClose.addEventListener('click', () => setMenuOpen(false));
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenuOpen(false)));
document.addEventListener('keydown', e => {
  if (menu.hidden) return;
  if (e.key === 'Escape') { e.preventDefault(); setMenuOpen(false); }
  if (e.key === 'Tab') {
    const items = [...menu.querySelectorAll('button, a[href]')];
    const first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});
window.addEventListener('resize', () => { if (window.innerWidth > 1100) setMenuOpen(false); });
document.getElementById('year').textContent = new Date().getFullYear();

// Show the mobile booking shortcut only once the hero CTA has scrolled away.
const bookingBar = document.querySelector('.mobile-booking-bar');
const heroBooking = document.querySelector('.hero [data-booking], .detail-hero [data-booking]');
const closingBooking = document.querySelector('.closing');
let bookingFrame = 0;
function updateBookingBar() {
  bookingFrame = 0;
  if (!bookingBar || !heroBooking) return;
  const headerBottom = document.querySelector('.site-header').getBoundingClientRect().bottom;
  const closingBounds = closingBooking?.getBoundingClientRect();
  const closingVisible = closingBounds && closingBounds.top < window.innerHeight - 80 && closingBounds.bottom > headerBottom;
  bookingBar.hidden = window.innerWidth > 600 || heroBooking.getBoundingClientRect().bottom > headerBottom || closingVisible;
}
function queueBookingBarUpdate() {
  if (!bookingFrame) bookingFrame = requestAnimationFrame(updateBookingBar);
}
window.addEventListener('scroll', queueBookingBarUpdate, { passive: true });
window.addEventListener('resize', queueBookingBarUpdate);
window.addEventListener('pageshow', queueBookingBarUpdate);
updateBookingBar();

// Shared, progressively enhanced portfolio lightbox (one set per gallery).
const portfolioSets = [...document.querySelectorAll('[data-portfolio-set]'), ...document.querySelectorAll('.portfolio-grid, .bridal-look-grid, .detail-gallery-grid')].filter(gallery => gallery.matches('[data-portfolio-set]') || !gallery.closest('[data-portfolio-set]'));
if (portfolioSets.length) {
  const english = document.documentElement.lang.startsWith('en');
  const icon = (path) => `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="${path}"/></svg>`;
  const lightbox = document.createElement('dialog');
  lightbox.className = 'portfolio-lightbox';
  lightbox.setAttribute('aria-label', english ? 'Portfolio photo gallery' : 'Galería de fotos del portafolio');
  lightbox.innerHTML = `<div class="lightbox-top"><span class="lightbox-count" aria-live="polite"></span><button type="button" class="lightbox-close" aria-label="${english ? 'Close gallery' : 'Cerrar galería'}"><span>${english ? 'Close' : 'Cerrar'}</span>${icon('m6 6 12 12M6 18 18 6')}</button></div><figure class="lightbox-figure"><img class="lightbox-image" alt=""/><figcaption class="lightbox-caption" aria-live="polite"></figcaption></figure><button type="button" class="lightbox-prev" aria-label="${english ? 'Previous photo' : 'Foto anterior'}">${icon('m14 5-7 7 7 7M7 12h14')}</button><button type="button" class="lightbox-next" aria-label="${english ? 'Next photo' : 'Foto siguiente'}">${icon('m10 5 7 7-7 7M3 12h14')}</button>`;
  document.body.append(lightbox);
  const viewerImage = lightbox.querySelector('.lightbox-image');
  const closeButton = lightbox.querySelector('.lightbox-close');
  let photos = [], current = 0, returnFocus = null, touchStart = null;
  function showPhoto(index) {
    current = (index + photos.length) % photos.length;
    const photo = photos[current];
    viewerImage.src = photo.src;
    viewerImage.alt = photo.alt;
    lightbox.querySelector('.lightbox-caption').textContent = photo.caption;
    lightbox.querySelector('.lightbox-count').textContent = `${current + 1} / ${photos.length}`;
    lightbox.querySelector('.lightbox-prev').hidden = photos.length < 2;
    lightbox.querySelector('.lightbox-next').hidden = photos.length < 2;
    const preload = new Image();
    preload.src = photos[(current + 1) % photos.length].src;
  }
  function closeLightbox() { lightbox.close(); }
  portfolioSets.forEach(gallery => {
    const figures = [...gallery.querySelectorAll('figure')].filter(f => f.querySelector('img'));
    const set = figures.map(figure => {
      const img = figure.querySelector('img');
      img.style.setProperty('--photo-ratio', `${img.getAttribute('width')} / ${img.getAttribute('height')}`);
      let trigger = figure.querySelector('a');
      if (!trigger) {
        trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'portfolio-lightbox-trigger';
        img.replaceWith(trigger);
        trigger.append(img);
      }
      trigger.setAttribute('aria-label', `${english ? 'View photo' : 'Ver foto'}: ${img.alt}`);
      trigger.setAttribute('aria-haspopup', 'dialog');
      figure.classList.add('has-lightbox');
      const caption = figure.querySelector('figcaption')?.cloneNode(true);
      caption?.querySelector('span')?.remove();
      return { src: trigger.tagName === 'A' ? trigger.href : img.src, alt: img.alt, caption: caption?.textContent.trim() || img.alt, trigger, figure };
    });
    set.forEach((photo, index) => photo.figure.addEventListener('click', event => {
      event.preventDefault();
      photos = set; returnFocus = photo.trigger;
      showPhoto(index);
      lightbox.showModal();
      document.documentElement.classList.add('lightbox-open');
      document.body.classList.add('lightbox-open');
      closeButton.focus({ preventScroll: true });
    }));
  });
  closeButton.addEventListener('click', closeLightbox);
  lightbox.querySelector('.lightbox-prev').addEventListener('click', () => showPhoto(current - 1));
  lightbox.querySelector('.lightbox-next').addEventListener('click', () => showPhoto(current + 1));
  lightbox.addEventListener('click', event => { if (event.target === lightbox) closeLightbox(); });
  lightbox.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight') { event.preventDefault(); showPhoto(current + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); showPhoto(current - 1); }
    if (event.key === 'Tab') {
      const controls = [...lightbox.querySelectorAll('button')].filter(b => !b.hidden);
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  lightbox.addEventListener('close', () => {
    document.documentElement.classList.remove('lightbox-open');
    document.body.classList.remove('lightbox-open');
    returnFocus?.focus({ preventScroll: true });
  });
  viewerImage.addEventListener('touchstart', event => { touchStart = event.touches.length === 1 ? { x: event.touches[0].clientX, y: event.touches[0].clientY } : null; }, { passive: true });
  viewerImage.addEventListener('touchend', event => {
    if (!touchStart || event.changedTouches.length !== 1) return;
    const dx = event.changedTouches[0].clientX - touchStart.x, dy = event.changedTouches[0].clientY - touchStart.y;
    if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.5) showPhoto(current + (dx < 0 ? 1 : -1));
    touchStart = null;
  }, { passive: true });
}

// Reveal extra bridal photos below the initial masonry without reordering it.
document.querySelectorAll('[data-portfolio-set]').forEach(section => {
  const button = section.querySelector('[data-gallery-toggle]');
  const more = section.querySelector('.gallery-more');
  const summary = section.querySelector('[data-gallery-summary]');
  if (!button || !more) return;
  const total = section.querySelectorAll('figure').length;
  const initial = Number(section.dataset.initialCount || 6);
  const english = document.documentElement.lang.startsWith('en');
  const photoType = section.dataset.photoType === 'makeup' ? (english ? 'makeup photos' : 'fotos de maquillaje') : (english ? 'bridal photos' : 'fotos de novias');
  function setExpanded(expanded) {
    more.hidden = !expanded;
    button.setAttribute('aria-expanded', String(expanded));
    button.querySelector('span').textContent = expanded ? button.dataset.hideLabel : button.dataset.showLabel;
    summary.textContent = english ? `Showing ${expanded ? total : initial} of ${total} ${photoType}` : `Mostrando ${expanded ? total : initial} de ${total} ${photoType}`;
  }
  setExpanded(false);
  button.hidden = false;
  button.addEventListener('click', () => setExpanded(button.getAttribute('aria-expanded') !== 'true'));
});

// Justified bridal rows preserve full photo proportions and fill every row.
const justifiedGalleryRecords = new WeakMap();
function layoutJustifiedGallery(gallery) {
  const width = gallery.clientWidth;
  if (!width) return;
  let record = justifiedGalleryRecords.get(gallery);
  if (!record) {
    record = { figures: [...gallery.querySelectorAll('figure')], width: 0 };
    justifiedGalleryRecords.set(gallery, record);
  }
  if (Math.abs(record.width - width) < 0.5) return;
  record.width = width;
  const figures = record.figures;
  const ratios = figures.map(f => {
    const img = f.querySelector('img');
    return Number(img.getAttribute('width')) / Number(img.getAttribute('height'));
  });
  const gap = width <= 600 ? 12 : 20;
  const target = width <= 600 ? Math.min(220, Math.max(160, width * .55)) : Math.min(420, width * .36);
  const maxPerRow = width < 600 ? 3 : width < 1000 ? 4 : 5;
  const costs = Array(figures.length + 1).fill(Infinity);
  const next = Array(figures.length).fill(0);
  costs[figures.length] = 0;
  for (let start = figures.length - 1; start >= 0; start--) {
    let sum = 0;
    for (let end = start; end < Math.min(figures.length, start + maxPerRow); end++) {
      sum += ratios[end];
      const count = end - start + 1;
      const height = (width - gap * (count - 1)) / sum;
      const penalty = Math.log(height / target) ** 2 + (height > target * 1.8 ? 3 : 0) + (count === 1 ? .3 : 0);
      if (penalty + costs[end + 1] < costs[start]) {
        costs[start] = penalty + costs[end + 1];
        next[start] = end + 1;
      }
    }
  }
  const fragment = document.createDocumentFragment();
  for (let start = 0; start < figures.length; start = next[start]) {
    const end = next[start];
    const sum = ratios.slice(start, end).reduce((a, b) => a + b, 0);
    const height = (width - gap * (end - start - 1)) / sum;
    const row = document.createElement('div');
    row.className = 'justified-row';
    row.style.setProperty('--justified-gap', `${gap}px`);
    for (let index = start; index < end; index++) {
      figures[index].style.setProperty('--tile-width', `${height * ratios[index]}px`);
      row.append(figures[index]);
    }
    fragment.append(row);
  }
  gallery.replaceChildren(fragment);
  gallery.classList.add('justified-gallery');
}
document.querySelectorAll('[data-portfolio-set] .bridal-look-grid, .quince-showcase .bridal-look-grid').forEach(gallery => {
  layoutJustifiedGallery(gallery);
  let frame = 0;
  new ResizeObserver(() => {
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      layoutJustifiedGallery(gallery);
    });
  }).observe(gallery);
});
