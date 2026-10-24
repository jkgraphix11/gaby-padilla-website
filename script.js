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
function setMenuOpen(open) {
  menu.hidden = !open;
  toggle.setAttribute('aria-expanded', String(open));
}
toggle.addEventListener('click', () => setMenuOpen(menu.hidden));
menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenuOpen(false)));
document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenuOpen(false); });
window.addEventListener('resize', () => { if (window.innerWidth > 1100) setMenuOpen(false); });
document.getElementById('year').textContent = new Date().getFullYear();
