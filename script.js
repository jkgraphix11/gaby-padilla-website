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
