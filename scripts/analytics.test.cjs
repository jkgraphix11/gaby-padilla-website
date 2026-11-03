const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../analytics.js'), 'utf8');

function page({ url = 'https://gabypadillamakeup.com/', gpc = false, dnt, disabled = false } = {}) {
  const scripts = [], listeners = {}, cookieWrites = [], controls = {};
  const location = new URL(url);
  let reloads = 0;
  location.reload = () => reloads++;
  const status = { textContent: '' };
  const storage = new Map(disabled ? [['gaby_analytics_disabled', 'true']] : []);
  const document = {
    documentElement: { lang: 'es-MX' },
    referrer: 'https://www.google.com/search?q=private@example.com',
    head: { appendChild: script => scripts.push(script) },
    createElement: () => ({}),
    addEventListener: (type, handler) => { listeners[type] = handler; },
    getElementById: () => status,
    querySelectorAll: () => ['off', 'on'].map(value => ({
      dataset: { analyticsPreference: value },
      addEventListener: (_, handler) => { controls[value] = handler; }
    }))
  };
  Object.defineProperty(document, 'cookie', {
    get: () => '_ga=private-cookie; _ga_6SEBFKV22M=private-session; unrelated=keep',
    set: value => cookieWrites.push(value)
  });
  const context = { document, location, navigator: { globalPrivacyControl: gpc, doNotTrack: dnt },
    localStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) },
    URL, URLSearchParams, window: {} };
  vm.createContext(context);
  const run = () => vm.runInContext(source, context);
  run();
  const calls = () => JSON.parse(JSON.stringify((context.window.dataLayer || []).map(call => Array.from(call))));
  const click = (href, service = '', placement = 'page') => {
    const link = { href, getAttribute: () => service, closest: name => name === placement ? {} : null };
    listeners.click?.({ target: { closest: () => link } });
  };
  return { scripts, calls, click, controls, cookieWrites, status, storage, run, reloads: () => reloads };
}

test('production initializes once and strips private URL/referrer details', () => {
  const p = page({url:'https://gabypadillamakeup.com/?utm_source=chatgpt.com&email=private%40example.com&text=secret#private'});
  p.run();
  assert.equal(p.scripts.length, 1);
  assert.match(p.scripts[0].src, /id=G-6SEBFKV22M$/);
  const config = p.calls().find(call => call[0] === 'config')[2];
  assert.equal(config.page_location, 'https://gabypadillamakeup.com/?utm_source=chatgpt.com');
  assert.equal(config.page_referrer, 'https://www.google.com/');
  assert.equal(config.allow_google_signals, false);
  assert.equal(config.allow_ad_personalization_signals, false);
  assert.equal(p.calls().filter(call => call[0] === 'config').length, 1);
});

test('staging, local previews and unrecognized paths never load Google Analytics', () => {
  for (const url of ['http://localhost:3000/', 'https://jkgraphix11.github.io/gaby-padilla-website/',
    'https://gabypadillamakeup.com/unknown/private@example.com']) assert.equal(page({url}).scripts.length, 0);
});

test('browser privacy signals and saved opt-outs prevent all collection', () => {
  for (const options of [{gpc:true}, {dnt:'1'}, {disabled:true}]) {
    const p = page(options);
    assert.equal(p.scripts.length, 0);
    assert.equal(p.calls().length, 0);
    assert.ok(p.cookieWrites.length > 0);
    assert.ok(p.cookieWrites.every(value => value.startsWith('_ga')));
  }
});

test('click events contain categories, never telephone numbers or message/order content', () => {
  const p = page();
  p.click('https://wa.me/526643867831?text=PRIVATE_ORDER_NAME');
  p.click('https://gabypadillamakeupartist.site.agendapro.com/mx/sucursal/578261', 'bridal', 'header');
  p.click('tel:+526643867831', '', 'footer');
  p.click('https://www.instagram.com/gabypadillamakeup/');
  const events = p.calls().filter(call => call[0] === 'event');
  assert.deepEqual(events.map(call => call[1]), ['whatsapp_click', 'booking_click', 'phone_click']);
  assert.equal(events[1][2].service_type, 'bridal');
  assert.equal(events[1][2].link_placement, 'header');
  assert.equal(events[2][2].link_placement, 'footer');
  assert.doesNotMatch(JSON.stringify(events), /PRIVATE_ORDER_NAME|526643867831|\?text=|578261/);
});

test('opting out stops subsequent events and persists the preference', () => {
  const p = page();
  p.controls.off();
  p.click('https://wa.me/526643867831');
  assert.equal(p.calls().filter(call => call[0] === 'event').length, 0);
  assert.equal(p.storage.get('gaby_analytics_disabled'), 'true');
  assert.ok(p.cookieWrites.length > 0);
  p.controls.on();
  assert.equal(p.storage.get('gaby_analytics_disabled'), 'false');
  assert.equal(p.reloads(), 1);
});
