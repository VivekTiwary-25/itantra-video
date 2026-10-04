/* Deterministic, dependency-free DOM helpers for iTantra v3 glass. */
(function (global) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const paths = {
    tower: '<path d="M12 21V5m-5 16h10M9 21l3-10 3 10M9 8a4 4 0 0 1 6 0M6 5a8 8 0 0 1 12 0"/>',
    'mobile-data': '<path d="M7 20V9m0 0-3 3m3-3 3 3M17 4v11m0 0-3-3m3 3 3-3"/><path d="M4 21h16"/>',
    wifi: '<path d="M2 9a15 15 0 0 1 20 0M5 12a11 11 0 0 1 14 0M8 15a6 6 0 0 1 8 0"/><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/>',
    internet: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 4 6 4 9s-1 6-4 9M12 3c-3 3-4 6-4 9s1 6 4 9"/>',
    bluetooth: '<path d="M12 2v20l7-6-14-8m0 8L19 8l-7-6"/>',
    lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 4v3"/>',
    mic: '<rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 11a7 7 0 0 0 14 0m-7 7v4m-4 0h8"/>',
    speaker: '<path d="M4 9h4l5-4v14l-5-4H4zM17 9a4 4 0 0 1 0 6m2-9a8 8 0 0 1 0 12"/>',
    phone: '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M10 5h4m-2 14h.01"/>'
  };
  function node(tag, attrs) {
    const el = document.createElementNS(NS, tag);
    for (const key in attrs) el.setAttribute(key, attrs[key]);
    return el;
  }
  function phone(target, options) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) throw new Error('Glass.phone: target element required');
    const opts = options || {};
    if (!opts.src || !['img', 'video'].includes(opts.kind)) throw new Error('Glass.phone: src and kind img|video required');
    el.replaceChildren();
    el.classList.add('glass-phone');
    const media = document.createElement(opts.kind);
    media.className = 'glass-phone-screen';
    media.src = opts.src;
    media.alt = opts.kind === 'img' ? (opts.alt || '') : undefined;
    if (opts.kind === 'video') { media.muted = true; media.playsInline = true; media.preload = 'auto'; }
    el.append(media);
    const camera = document.createElement('span');
    camera.className = 'glass-phone-camera';
    camera.setAttribute('aria-hidden', 'true');
    el.append(camera);
    return el;
  }
  function icon(name) {
    if (!Object.prototype.hasOwnProperty.call(paths, name)) throw new Error('Glass.icon: unknown icon ' + name);
    const svg = node('svg', {viewBox:'0 0 24 24', class:'glass-icon', 'aria-hidden':'true'});
    svg.innerHTML = paths[name];
    return svg;
  }
  function cross(target, progress) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) throw new Error('Glass.cross: target element required');
    el.classList.add('glass-cross-host');
    let svg = el.querySelector(':scope > .glass-cross');
    if (!svg) {
      svg = node('svg', {viewBox:'0 0 100 100', class:'glass-cross', 'aria-hidden':'true'});
      const under = node('path', {d:'M12 84 L88 16', fill:'none', stroke:'rgba(255,255,255,.94)', 'stroke-width':'10', 'stroke-linecap':'round'});
      const red = node('path', {d:'M12 84 L88 16', fill:'none', stroke:'#ff4d5e', 'stroke-width':'6', 'stroke-linecap':'round'});
      svg.append(under, red);
      el.append(svg);
    }
    const p = Math.max(0, Math.min(1, Number(progress) || 0));
    for (const line of svg.querySelectorAll('path')) {
      line.style.strokeDasharray = '102';
      line.style.strokeDashoffset = String(102 * (1 - p));
    }
    return svg;
  }
  global.Glass = Object.freeze({phone, icon, cross});
})(window);
