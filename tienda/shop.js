'use strict';
const params = new URLSearchParams(location.search);
const preview = params.get('preview') === '1';
const lang = params.get('lang') === 'en' ? 'en' : 'es';
const t = (es, en) => lang === 'en' ? en : es;
const money = value => new Intl.NumberFormat(lang === 'en' ? 'en-US' : 'es-MX', {style: 'currency', currency: 'MXN', currencyDisplay: 'narrowSymbol', maximumFractionDigits: 2}).format(value);
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const localized = (p, field) => lang === 'en' ? p[field + '_en'] || p[field] : p[field];
const label = p => localized(p, 'name');
const productDialog = document.getElementById('product-dialog');
const messageDialog = document.getElementById('message-dialog');
let catalog, selected, category = 'all';
function translate() {
 document.documentElement.lang = lang === 'en' ? 'en' : 'es-MX';
 document.querySelectorAll('[data-es]').forEach(el => el.innerHTML = el.dataset[lang]);
}
translate();
document.getElementById('year').textContent = new Date().getFullYear();
document.getElementById('preview-bar').hidden = !preview;
document.getElementById('language').href = `?lang=${lang === 'en' ? 'es' : 'en'}${preview ? '&preview=1' : ''}`;
document.getElementById('language').textContent = lang === 'en' ? 'ES ↗' : 'EN ↗';
document.getElementById('shop-home').href = `./${location.search}`;
document.getElementById('manage-link').href = `manage.html?preview=1&lang=${lang}`;
function imageURL(p) {
 if (preview && /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(p.image)) return p.image;
 const url = new URL(p.image, location.href);
 return url.origin === location.origin && !url.pathname.includes('..') && /\.(svg|webp|png|jpe?g)$/i.test(url.pathname) ? url.href : 'assets/serum.svg';
}
function priceLabel(p) {
 return p.price == null ? t('Precio por confirmar', 'Price to confirm') : money(p.price) + ' <small>MXN</small>';
}
function stockLabel(p) {
 if (p.quantity == null) return t('Consultar disponibilidad', 'Ask about availability');
 return p.quantity === 0 ? t('Agotado', 'Sold out') : p.quantity === 1 ? t('Última pieza', 'Last one') : t(`${p.quantity} piezas disponibles`, `${p.quantity} available`);
}
function buyLabel(p) {
 return p.quantity === 0 ? t('Preguntar si volverá ↗', 'Ask about restocking ↗') : t('Comprar por WhatsApp ↗', 'Buy via WhatsApp ↗');
}
function render() {
 const products = catalog.products.filter(p => (p.state === 'published' || preview && p.state === 'draft') && (category === 'all' || p.category === category) && (!document.getElementById('in-stock').checked || p.quantity > 0));
 document.getElementById('catalog-status').textContent = preview ? t(`${products.length} productos · Precios en MXN · Vista previa`, `${products.length} products · Prices in MXN · Preview`) : t(`${products.length} productos · Precios en MXN`, `${products.length} products · Prices in MXN`);
 document.getElementById('product-grid').innerHTML = products.map(p => `
  <article class="product-card ${p.quantity === 0 ? 'sold' : ''}">
   <button type="button" class="product-art" data-product="${escapeHTML(p.id)}" aria-label="${escapeHTML(t('Ver ', 'View ') + label(p))}">
    <span class="stock-badge">${stockLabel(p)}</span>
    <img src="${escapeHTML(imageURL(p))}" alt="${escapeHTML(label(p))}" width="400" height="500" loading="lazy">
   </button>
   <p class="product-brand">${escapeHTML(p.brand)}</p>
   <h3 class="product-title"><button type="button" data-product="${escapeHTML(p.id)}">${escapeHTML(label(p))}</button></h3>
   <p class="product-size">${escapeHTML(localized(p, 'size'))}</p>
   <p class="product-summary">${escapeHTML((localized(p, 'description') || '').split('. ')[0])}.</p>
   <div class="product-bottom"><span class="product-price">${priceLabel(p)}</span><button type="button" class="product-more" data-product="${escapeHTML(p.id)}">${t('Ver detalles ↗', 'View details ↗')}</button></div>
   <a class="whatsapp-button product-buy" data-buy="${escapeHTML(p.id)}" href="${escapeHTML(makeLink(orderMessage(p)))}" target="_blank" rel="noopener noreferrer" aria-label="${escapeHTML(buyLabel(p) + ' · ' + label(p))}">${buyLabel(p)}</a>
  </article>`).join('') || `<p class="empty-state">${t('Por ahora no hay productos en esta selección. Pregunta a Gaby por WhatsApp.', 'No products in this selection right now. Ask Gaby on WhatsApp.')}</p>`;
}
function openProduct(id) {
 selected = catalog.products.find(p => p.id === id && (p.state === 'published' || preview && p.state === 'draft'));
 if (!selected) return;
 const p = selected;
 document.getElementById('product-detail').innerHTML = `
  <div class="detail-layout">
   <div class="detail-image"><img src="${escapeHTML(imageURL(p))}" alt="${escapeHTML(label(p))}" width="400" height="500"></div>
   <div class="detail-copy">
    <span class="eyebrow">${escapeHTML(p.brand)}</span>
    <h2 id="detail-title">${escapeHTML(label(p))}</h2>
    <p class="detail-size">${escapeHTML(localized(p, 'size'))}</p>
    <p class="detail-description">${escapeHTML(localized(p, 'description'))}</p>
    ${p.image_note ? `<p class="detail-note">${escapeHTML(localized(p, 'image_note'))}</p>` : ''}
    <p class="detail-price">${priceLabel(p)}</p>
    <p class="detail-stock">${stockLabel(p)}</p>
    ${p.quantity > 0 ? `<label for="order-quantity">${t('Cantidad', 'Quantity')}</label><select id="order-quantity">${Array.from({length: Math.min(p.quantity, 99)}, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}</select>` : ''}
    <a href="${escapeHTML(makeLink(orderMessage(p)))}" id="order-product" class="whatsapp-button" target="_blank" rel="noopener noreferrer">${buyLabel(p)}</a>
    <p class="detail-note">${t('Confirmamos disponibilidad, total, pago y entrega por WhatsApp. Tu mensaje no reserva el producto.', 'We confirm availability, total, payment, and delivery on WhatsApp. Your message does not reserve this product.')}</p>
   </div>
  </div>`;
 const order = document.getElementById('order-product');
 document.getElementById('order-quantity')?.addEventListener('change', e => order.href = makeLink(orderMessage(p, Number(e.target.value))));
 order.addEventListener('click', e => {
  if (preview) {
   e.preventDefault();
   showMessage(orderMessage(p, Number(document.getElementById('order-quantity')?.value || 1)));
  }
 });
 if (!productDialog.open) productDialog.showModal();
}
function orderMessage(p, q = 1) {
 const url = new URL(location.href);
 url.search = '';
 url.hash = p.id;
 if (p.quantity === 0) return t(`¡Hola, Gaby! Me interesa ${p.name}. ¿Me avisas si vuelve a estar disponible?\n\n${url.href}`, `Hi Gaby! I’m interested in ${label(p)}. Could you let me know if it becomes available again?\n\n${url.href}`);
 const price = p.price == null ? t('Precio por confirmar', 'Price to confirm') : `${money(p.price)} MXN`;
 const subtotal = p.price == null ? '' : t(`\nSubtotal de productos: ${money(p.price * q)} MXN`, `\nProduct subtotal: ${money(p.price * q)} MXN`);
 return t(`¡Hola, Gaby! Me gustaría pedir:\n\n${q} × ${p.name}\nPresentación: ${p.size}\nPrecio por pieza: ${price}${subtotal}\n\n¿Sigue disponible? ¿Cómo coordinamos el pago y la entrega en Tijuana?\n\n${url.href}`, `Hi Gaby! I’d like to order:\n\n${q} × ${label(p)}\nSize / shade: ${localized(p, 'size')}\nUnit price: ${price}${subtotal}\n\nIs it still available? How can we arrange payment and delivery in Tijuana?\n\n${url.href}`);
}
function makeLink(message) { return `https://wa.me/${catalog.whatsapp}?text=${encodeURIComponent(message)}`; }
function showMessage(message) {
 document.getElementById('prepared-message').textContent = message;
 if (productDialog.open) productDialog.close();
 messageDialog.showModal();
}
function loadPreviewState(base) {
 try {
  const saved = JSON.parse(sessionStorage.getItem('gaby-shop-demo'));
  return saved?.version === base.previewVersion && Array.isArray(saved.products) ? {...base, products: saved.products} : base;
 } catch { return base; }
}
async function load() {
 try {
  const response = await fetch(preview ? 'instagram-catalog.json' : '/api/catalog', {cache: 'no-store'});
  if (!response.ok) throw Error('Unavailable');
  catalog = await response.json();
  if (preview) catalog = loadPreviewState(catalog);
 } catch {
  if (preview) {
   document.getElementById('catalog-status').textContent = t('No se pudo cargar la vista previa. Intenta de nuevo.', 'Could not load the preview. Please try again.');
   return;
  }
  try {
   const r = await fetch('catalog.json', {cache: 'no-store'});
   if (!r.ok) throw Error();
   catalog = await r.json();
  } catch {
   document.getElementById('catalog-status').textContent = t('No se pudo cargar el catálogo. Escríbenos por WhatsApp.', 'Could not load the catalog. Please contact us on WhatsApp.');
   catalog = {products: [], whatsapp: '526643867831'};
  }
 }
 document.getElementById('general-whatsapp').href = makeLink(t('¡Hola, Gaby! Estoy buscando un producto. ¿Me ayudas?', 'Hi Gaby! I’m looking for a product. Can you help?'));
 render();
 if (location.hash) openProduct(decodeURIComponent(location.hash.slice(1)));
}
document.getElementById('product-grid').addEventListener('click', e => {
 const buy = e.target.closest('[data-buy]');
 if (buy) {
  if (preview) {
   e.preventDefault();
   selected = catalog.products.find(p => p.id === buy.dataset.buy);
   showMessage(orderMessage(selected));
  }
  return;
 }
 const button = e.target.closest('[data-product]');
 if (button) openProduct(button.dataset.product);
});
document.querySelectorAll('[data-category]').forEach(b => b.addEventListener('click', () => {
 category = b.dataset.category;
 document.querySelectorAll('[data-category]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
 render();
}));
document.getElementById('in-stock').addEventListener('change', render);
document.getElementById('close-detail').addEventListener('click', () => productDialog.close());
document.getElementById('close-message').addEventListener('click', () => messageDialog.close());
document.getElementById('back-to-detail').addEventListener('click', () => {
 messageDialog.close();
 if (selected) openProduct(selected.id);
});
document.getElementById('general-whatsapp').addEventListener('click', e => {
 if (preview) {
  e.preventDefault();
  selected = null;
  showMessage(t('¡Hola, Gaby! Estoy buscando un producto. ¿Me ayudas?', 'Hi Gaby! I’m looking for a product. Can you help?'));
 }
});
window.addEventListener('pageshow', e => { if (e.persisted) load(); });
load();
