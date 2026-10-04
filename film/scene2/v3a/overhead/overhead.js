(function (global) {
  'use strict';
  const W = 1920, H = 1080;
  const V = { lat: 12.37247, lon: 76.58497 };
  const Y = { lat: 12.37125, lon: 76.58620 };
  const METRES_PER_DEG = 111195;
  const MID_LAT = (V.lat + Y.lat) / 2;
  const MID_LON = (V.lon + Y.lon) / 2;
  const PX_PER_METRE = 3.05;
  const S = 'http://www.w3.org/2000/svg';
  let state = null;

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const progress = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
  const smooth = p => p * p * (3 - 2 * p);
  const mix = (a, b, p) => a + (b - a) * p;
  const xy = (lat, lon) => [
    W / 2 + (lon - MID_LON) * METRES_PER_DEG * Math.cos(MID_LAT * Math.PI / 180) * PX_PER_METRE,
    H / 2 - (lat - MID_LAT) * METRES_PER_DEG * PX_PER_METRE
  ];
  const path = points => points.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(2)} ${p[1].toFixed(2)}`).join(' ');
  function svgNode(tag, attrs, parent) {
    const n = document.createElementNS(S, tag);
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, String(v)));
    parent.appendChild(n);
    return n;
  }
  function mercatorPoint(geo, point) {
    const scale = 256 * Math.pow(2, geo.frame.zoom);
    const wx = geo.frame.origin_world_px[0] + point[0];
    const wy = geo.frame.origin_world_px[1] + point[1];
    const lon = wx / scale * 360 - 180;
    const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * wy / scale))) * 180 / Math.PI;
    return xy(lat, lon);
  }
  function drawBuilding(group, outline, converted) {
    if (converted.length < 3) return;
    const d = path(converted) + ' Z';
    svgNode('path', { d, class: 'building-side', transform: 'translate(10 14)' }, group);
    for (let i = 0; i < converted.length; i++) {
      const a = converted[i], b = converted[(i + 1) % converted.length];
      if (b[1] < a[1] - 3) continue;
      const wall = path([a, b, [b[0] + 10, b[1] + 14], [a[0] + 10, a[1] + 14]]) + ' Z';
      svgNode('path', { d: wall, class: 'building-wall' }, group);
    }
    svgNode('path', { d, class: 'building-roof' }, group);
    if (outline.court) {
      const court = outline.court.map(p => mercatorPoint(state.geo.outlines, p));
      svgNode('path', { d: path(court) + ' Z', class: 'court' }, group);
    }
  }
  function buildMap(svg, geo) {
    const overflow = { 'data-layout-allow-overflow': '' };
    const land = svgNode('g', overflow, svg);
    const green = svgNode('g', overflow, svg);
    const roads = svgNode('g', overflow, svg);
    const context = svgNode('g', { ...overflow, class: 'building-context' }, svg);
    const buildings = svgNode('g', overflow, svg);
    const routeLayer = svgNode('g', {}, svg);
    for (const e of geo.osm.elements) {
      if (!e.geometry || !e.tags) continue;
      const pts = e.geometry.map(p => xy(p.lat, p.lon));
      if (e.tags.amenity === 'college') svgNode('path', { d: path(pts) + ' Z', class: 'campus-land' }, land);
      if (e.tags.highway) svgNode('path', { d: path(pts), class: `path ${e.tags.highway}` }, roads);
    }
    const outline = geo.outlines;
    const convert = p => mercatorPoint(outline, p);
    for (const e of outline.features) {
      if (e.pts) svgNode('path', { d: path(e.pts.map(convert)) + ' Z', class: e.id === 'cricket_pitch' ? 'court' : 'green' }, green);
      else if (e.center) {
        const c = convert(e.center), r = convert([e.center[0] + e.rx, e.center[1] + e.ry]);
        svgNode('ellipse', { cx: c[0], cy: c[1], rx: Math.abs(r[0] - c[0]), ry: Math.abs(r[1] - c[1]), class: 'green' }, green);
      }
    }
    for (const e of outline.context) drawBuilding(context, e, e.pts.map(convert));
    for (const e of outline.campus) drawBuilding(buildings, e, e.pts.map(convert));
    const routeD = path([xy(V.lat, V.lon), xy(Y.lat, Y.lon)]);
    const under = svgNode('path', { d: routeD, class: 'route-under' }, routeLayer);
    const route = svgNode('path', { d: routeD, class: 'route' }, routeLayer);
    return { route, under };
  }
  function pin(className, label, at, map) {
    const el = document.createElement('div');
    el.className = `overhead-map-pin ${className}`;
    const p = xy(at.lat, at.lon);
    el.style.left = `${p[0]}px`;
    el.style.top = `${p[1]}px`;
    el.innerHTML = `<div class="ring"></div><div class="dot"></div><div class="label-pin" data-layout-allow-overflow>${label}</div>`;
    map.appendChild(el);
    return el;
  }
  function mount(el, opts) {
    if (!el || !opts || !opts.walkStill || !opts.yashStill) throw new Error('Overhead.mount needs el, walkStill and yashStill');
    const geo = opts.geo || global.OVERHEAD_GEO;
    if (!geo || !geo.osm || !geo.outlines) throw new Error('Overhead.mount needs local campus geo data');
    el.replaceChildren();
    el.classList.add('overhead-stage');
    const camera = document.createElement('div'); camera.className = 'overhead-map-camera';
    const svg = svgNode('svg', { class: 'overhead-map', viewBox: `0 0 ${W} ${H}`, 'aria-label': 'NIE North Campus overhead map', 'data-layout-allow-overflow': '' }, camera);
    el.appendChild(camera);
    state = { el, geo, camera };
    const paths = buildMap(svg, geo);
    state.route = paths.route;
    state.routeUnder = paths.under;
    state.vachana = pin('vachana', 'Vachana', V, camera);
    state.yash = pin('yash', 'Yash', Y, camera);
    state.walk = document.createElement('img'); state.walk.className = 'overhead-walk'; state.walk.src = opts.walkStill; state.walk.alt = '';
    state.distance = document.createElement('div'); state.distance.className = 'glass-panel overhead-distance'; state.distance.textContent = '~300 m, walking distance';
    state.yashImage = document.createElement('img'); state.yashImage.className = 'overhead-yash'; state.yashImage.src = opts.yashStill; state.yashImage.alt = '';
    el.append(state.walk, state.distance, state.yashImage);
    render(0);
    return state;
  }
  function render(seconds) {
    if (!state) return;
    const t = clamp(Number(seconds) || 0, 0, 5);
    const rise = smooth(progress(t, 0, .8));
    const dive = smooth(progress(t, 3.4, 5));
    const v = xy(V.lat, V.lon), y = xy(Y.lat, Y.lon);
    const startZoom = 2.65;
    const earlyZoom = mix(startZoom, 1, rise);
    const finalZoom = mix(1, 5.2, dive);
    const zoom = t <= .8 ? earlyZoom : finalZoom;
    const earlyX = mix(W / 2 - v[0] * startZoom, 0, rise);
    const earlyY = mix(H / 2 - v[1] * startZoom, 0, rise);
    const finalX = (W / 2 - y[0] * finalZoom) * dive;
    const finalY = (H / 2 - y[1] * finalZoom) * dive;
    state.camera.style.transform = `translate(${(t <= .8 ? earlyX : finalX).toFixed(2)}px, ${(t <= .8 ? earlyY : finalY).toFixed(2)}px) scale(${zoom.toFixed(5)})`;
    state.camera.style.opacity = String(smooth(progress(t, 0, .58)) * (1 - smooth(progress(t, 4.05, 5))));

    const walkScale = mix(1, .32, rise);
    state.walk.style.transform = `translate(${((v[0] - W / 2) * rise).toFixed(1)}px, ${((v[1] - H / 2) * rise).toFixed(1)}px) scale(${walkScale.toFixed(4)}) rotateX(${(42 * rise).toFixed(2)}deg)`;
    state.walk.style.opacity = String(1 - smooth(progress(t, .51, .88)));
    state.walk.style.visibility = t >= .88 ? 'hidden' : 'visible';

    const pinIn = smooth(progress(t, .85, 1.16));
    state.vachana.style.opacity = String(pinIn * (1 - smooth(progress(t, 3.65, 4.1))));
    state.yash.style.opacity = String(smooth(progress(t, 1.04, 1.30)) * (1 - smooth(progress(t, 4.05, 4.6))));
    const lineP = smooth(progress(t, 1.02, 1.8));
    const clip = `inset(0 ${(100 * (1 - lineP)).toFixed(2)}% 0 0)`;
    const routeOpacity = String(pinIn * (1 - smooth(progress(t, 3.65, 4.15))));
    state.route.style.clipPath = clip;
    state.routeUnder.style.clipPath = clip;
    state.route.style.opacity = routeOpacity;
    state.routeUnder.style.opacity = routeOpacity;
    state.distance.style.opacity = String(smooth(progress(t, 1.18, 1.40)) * (1 - smooth(progress(t, 3.82, 4.10))));
    state.distance.style.transform = `translateY(${(16 * (1 - smooth(progress(t, 1.18, 1.40)))).toFixed(1)}px)`;

    const reveal = smooth(progress(t, 4.02, 5));
    state.yashImage.style.opacity = String(reveal);
    state.yashImage.style.transform = `scale(${mix(1.16, 1, reveal).toFixed(5)})`;
    state.yashImage.style.visibility = t <= 4.02 ? 'hidden' : 'visible';
    state.yashImage.style.clipPath = t === 5 ? 'none' : `circle(${(145 * reveal).toFixed(2)}% at 50% 50%)`;
  }
  global.Overhead = { mount, render };
})(window);
