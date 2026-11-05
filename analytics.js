/* GA4 measurement for the production website. No advertising or form data. */
(() => {
  'use strict';
  const measurementId = 'G-6SEBFKV22M';
  const preferenceKey = 'gaby_analytics_disabled';
  const allowedPaths = new Set(['/', '/en/', '/novias/', '/xv-anos/', '/en/bridal/', '/en/quinceanera/', '/tienda/', '/privacidad/']);
  const browserOptOut = navigator.globalPrivacyControl === true || navigator.doNotTrack === '1';
  let optedOut = false;
  try { optedOut = localStorage.getItem(preferenceKey) === 'true'; } catch (_) { /* Storage is optional. */ }

  function showPreference() {
    const status = document.getElementById('analytics-status');
    if (status) status.textContent = browserOptOut
      ? 'Analítica desactivada por la configuración del navegador. / Analytics disabled by your browser privacy setting.'
      : optedOut ? 'Analítica desactivada en este navegador. / Analytics disabled in this browser.'
      : 'Analítica activada en este navegador. / Analytics enabled in this browser.';
  }
  function clearAnalyticsCookies() {
    document.cookie.split(';').map(part => part.trim().split('=')[0]).filter(name => /^_ga(?:_|$)/.test(name)).forEach(name => {
      for (const domain of ['', location.hostname, '.gabypadillamakeup.com']) {
        document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax${domain ? '; Domain=' + domain : ''}`;
      }
    });
  }
  document.querySelectorAll('[data-analytics-preference]').forEach(button => {
    button.addEventListener('click', () => {
      optedOut = button.dataset.analyticsPreference === 'off';
      try { localStorage.setItem(preferenceKey, String(optedOut)); } catch (_) { /* Current-page opt-out still works. */ }
      window['ga-disable-' + measurementId] = optedOut || browserOptOut;
      if (optedOut || browserOptOut) clearAnalyticsCookies();
      showPreference();
      if (!optedOut && !browserOptOut) location.reload();
    });
  });
  showPreference();
  window['ga-disable-' + measurementId] = optedOut || browserOptOut;
  if (optedOut || browserOptOut) { clearAnalyticsCookies(); return; }
  if (location.hostname !== 'gabypadillamakeup.com' || location.protocol !== 'https:') return;
  const path = location.pathname.replace(/index\.html$/, '');
  if (!allowedPaths.has(path) || window.__gabyAnalyticsInitialized) return;
  window.__gabyAnalyticsInitialized = true;

  // Send only known public paths and limited campaign attribution, never arbitrary query strings.
  const pageLocation = new URL(location.origin + path);
  const query = new URLSearchParams(location.search);
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign']) {
    const value = query.get(key);
    if (value && /^[a-z0-9._ -]{1,80}$/i.test(value) && !/\d{7,}/.test(value)) pageLocation.searchParams.set(key, value);
  }
  let pageReferrer = '';
  try { pageReferrer = new URL(document.referrer).origin + '/'; } catch (_) { /* Direct visit. */ }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    page_location: pageLocation.href,
    page_referrer: pageReferrer,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    ...(query.get('analytics_debug') === '1' ? { debug_mode: true } : {})
  });
  // Load the Google tag after the page is usable: first interaction, or idle time after load.
  // Commands queue in dataLayer until then, so no page view or click is lost.
  let tagLoaded = false;
  const loadTag = () => {
    if (tagLoaded) return;
    tagLoaded = true;
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.appendChild(tag);
  };
  if (typeof window.addEventListener !== 'function') {
    loadTag();
  } else {
    for (const type of ['pointerdown', 'keydown', 'scroll', 'touchstart']) {
      window.addEventListener(type, loadTag, { once: true, passive: true, capture: true });
    }
    const whenIdle = () => (window.requestIdleCallback ? window.requestIdleCallback(loadTag, { timeout: 3000 }) : setTimeout(loadTag, 2000));
    if (document.readyState === 'complete') whenIdle(); else window.addEventListener('load', whenIdle, { once: true });
  }

  document.addEventListener('click', event => {
    if (window['ga-disable-' + measurementId]) return;
    const link = event.target.closest?.('a[href]');
    if (!link) return;
    let url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    let eventName, destination;
    if (url.hostname === 'gabypadillamakeupartist.site.agendapro.com') {
      eventName = 'booking_click'; destination = 'agendapro';
    } else if (url.hostname === 'wa.me' || url.hostname === 'api.whatsapp.com') {
      eventName = 'whatsapp_click'; destination = 'whatsapp';
    } else if (url.protocol === 'tel:') {
      eventName = 'phone_click'; destination = 'phone';
    } else return;
    const service = link.getAttribute('data-booking') || (path === '/tienda/' ? 'shop' : 'general');
    const placement = link.closest('header') ? 'header' : link.closest('footer') ? 'footer' : 'page';
    window.gtag('event', eventName, {
      send_to: measurementId,
      destination,
      service_type: ['bridal', 'xv', 'shop', 'general'].includes(service) ? service : 'general',
      link_placement: placement,
      page_language: document.documentElement.lang.startsWith('en') ? 'en' : 'es',
      transport_type: 'beacon'
    });
  }, true);
})();
