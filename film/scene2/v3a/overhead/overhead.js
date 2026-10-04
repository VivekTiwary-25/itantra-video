(function (global) {
  'use strict';
  const W = 1920, H = 1080;
  const V = { lat: 12.37247, lon: 76.58497 };
  const Y = { lat: 12.37125, lon: 76.58620 };
  const METRES_PER_DEG = 111195;
  const MID_LAT = (V.lat + Y.lat) / 2;
  const MID_LON = (V.lon + Y.lon) / 2;
  const PX_PER_METRE = 4;
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
  const metres = (a, b) => Math.hypot(
    (a.lon - b.lon) * METRES_PER_DEG * Math.cos(MID_LAT * Math.PI / 180),
    (a.lat - b.lat) * METRES_PER_DEG
  );
  function walkingRoute(osm) {
    const graph = new Map(), segments = [];
    const key = p => `${p.lat.toFixed(7)},${p.lon.toFixed(7)}`;
    const points = new Map();
    function edge(a, b, length) {
      if (!graph.has(a)) graph.set(a, []);
      graph.get(a).push({ to: b, length });
    }
    for (const way of osm.elements) {
      if (!way.tags?.highway || !way.geometry) continue;
      for (let i = 1; i < way.geometry.length; i++) {
        const a = way.geometry[i - 1], b = way.geometry[i];
        const ak = key(a), bk = key(b), length = metres(a, b);
        points.set(ak, a); points.set(bk, b);
        edge(ak, bk, length); edge(bk, ak, length);
        segments.push({ a, b, ak, bk, length });
      }
    }
    function snap(pin) {
      let best = null;
      const p = xy(pin.lat, pin.lon);
      for (const segment of segments) {
        const a = xy(segment.a.lat, segment.a.lon), b = xy(segment.b.lat, segment.b.lon);
        const dx = b[0] - a[0], dy = b[1] - a[1];
        const t = clamp(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy), 0, 1);
        const point = { lat: mix(segment.a.lat, segment.b.lat, t), lon: mix(segment.a.lon, segment.b.lon, t) };
        const distance = metres(pin, point);
        if (!best || distance < best.distance) best = { segment, point, t, distance };
      }
      return best;
    }
    function connect(pin, name) {
      const at = snap(pin), road = `${name}-road`;
      points.set(name, pin); points.set(road, at.point);
      edge(name, road, at.distance); edge(road, name, at.distance);
      for (const [node, fraction] of [[at.segment.ak, at.t], [at.segment.bk, 1 - at.t]]) {
        const length = at.segment.length * fraction;
        edge(road, node, length); edge(node, road, length);
      }
    }
    connect(V, 'start'); connect(Y, 'end');
    const distance = new Map([['start', 0]]), previous = new Map(), open = new Set(['start']);
    while (open.size) {
      let current = null;
      for (const candidate of open) if (current === null || distance.get(candidate) < distance.get(current)) current = candidate;
      open.delete(current);
      if (current === 'end') break;
      for (const next of graph.get(current) || []) {
        const candidate = distance.get(current) + next.length;
        if (candidate < (distance.get(next.to) ?? Infinity)) {
          distance.set(next.to, candidate);
          previous.set(next.to, current);
          open.add(next.to);
        }
      }
    }
    if (!distance.has('end')) throw new Error('No connected OSM highway route between pins');
    const keys = [];
    for (let at = 'end'; at; at = previous.get(at)) keys.push(at);
    keys.reverse();
    return { points: keys.map(k => points.get(k)), lengthMetres: distance.get('end') };
  }
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
    const walked = walkingRoute(geo.osm);
    const routePoints = walked.points.map(p => xy(p.lat, p.lon));
    const routeD = path(routePoints);
    const mask = svgNode('mask', { id: 'overhead-route-reveal', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: W, height: H }, svg);
    const reveal = svgNode('path', { d: routeD, fill: 'none', stroke: '#fff', 'stroke-width': 24, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, mask);
    const under = svgNode('path', { d: routeD, class: 'route-under', mask: 'url(#overhead-route-reveal)' }, routeLayer);
    const route = svgNode('path', { d: routeD, class: 'route', mask: 'url(#overhead-route-reveal)' }, routeLayer);
    const length = reveal.getTotalLength();
    reveal.style.strokeDasharray = `${length} ${length}`;
    reveal.style.strokeDashoffset = String(length);
    let remaining = walked.lengthMetres / 2, middle = routePoints[0];
    for (let i = 1; i < routePoints.length; i++) {
      const a = walked.points[i - 1], b = walked.points[i], segment = metres(a, b);
      if (remaining <= segment) {
        middle = [mix(routePoints[i - 1][0], routePoints[i][0], remaining / segment), mix(routePoints[i - 1][1], routePoints[i][1], remaining / segment)];
        break;
      }
      remaining -= segment;
    }
    return { route, under, reveal, length, middle };
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
  function adopt(video, still, cls) {
    if (video) { video.classList.add(cls, 'overhead-live'); video.muted = true; video.playsInline = true; return video; }
    const img = document.createElement('img'); img.className = cls; img.src = still; img.alt = ''; return img;
  }
  function mount(el, opts) {
    if (!el || !opts || !(opts.walkVideo || opts.walkStill) || !(opts.yashVideo || opts.yashStill)) throw new Error('Overhead.mount needs el, walkVideo or walkStill, and yashVideo or yashStill');
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
    state.reveal = paths.reveal;
    state.routeLength = paths.length;
    state.vachana = pin('vachana', 'Vachana', V, camera);
    state.yash = pin('yash', 'Yash', Y, camera);
    // F0026: prefer the composition's live videos (already timed by HyperFrames) so no camera frame is ever held.
    state.walk = adopt(opts.walkVideo, opts.walkStill, 'overhead-walk');
    state.distance = document.createElement('div'); state.distance.className = 'glass-panel overhead-distance'; state.distance.textContent = '~300 m, walking distance';
    state.distance.style.left = `${paths.middle[0] + 44}px`;
    state.distance.style.top = `${paths.middle[1] - 138}px`;
    state.yashImage = adopt(opts.yashVideo, opts.yashStill, 'overhead-yash');
    state.live = { walk: !!opts.walkVideo, yash: !!opts.yashVideo };
    camera.appendChild(state.distance);
    el.append(state.walk, state.yashImage);
    render(0);
    return state;
  }
  function render(seconds) {
    if (!state) return;
    const t = clamp(Number(seconds) || 0, 0, 5);
    const rise = smooth(progress(t, 0, .8));
    const v = xy(V.lat, V.lon), y = xy(Y.lat, Y.lon);
    // F0050 (spec 005 S2): the rise is a tracking pull-back that travels FROM Vachana's pin TOWARD Yash's. The camera
    // centre glides from Vachana's pin to the map centre (the midpoint toward Yash) while it zooms out, so the walk
    // texture, held at the frame centre, moves down-right across the map toward Yash.
    const startZoom = 2.65;
    const cx = mix(v[0], W / 2, rise), cy = mix(v[1], H / 2, rise);
    const earlyZoom = Math.pow(startZoom, 1 - rise);
    // ONE smooth direct zoom onto Yash's pin: a single ease drives both the scale (exponential, so it feels even) and
    // the pin's glide to the frame centre. No overshoot, no second push.
    const dive = smooth(progress(t, 3.4, 5));
    const finalZoom = Math.pow(5.2, dive);
    const pinX = mix(y[0], W / 2, dive), pinY = mix(y[1], H / 2, dive);
    const zoom = t <= .8 ? earlyZoom : finalZoom;
    const tx = t <= .8 ? W / 2 - cx * earlyZoom : pinX - y[0] * finalZoom;
    const ty = t <= .8 ? H / 2 - cy * earlyZoom : pinY - y[1] * finalZoom;
    state.camera.style.transform = `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${zoom.toFixed(5)})`;
    state.camera.style.opacity = String(smooth(progress(t, 0, .58)) * (1 - smooth(progress(t, 4.05, 5))));

    const walkScale = mix(1, .32, rise);
    const drift = 70 * rise;  // a little extra travel down-right, along the route direction
    state.walk.style.transform = `translate(${drift.toFixed(1)}px, ${(drift * (y[1] - v[1]) / (y[0] - v[0])).toFixed(1)}px) scale(${walkScale.toFixed(4)}) rotateX(${(42 * rise).toFixed(2)}deg)`;
    state.walk.style.opacity = String(1 - smooth(progress(t, .51, .88)));
    state.walk.style.visibility = t >= .88 ? 'hidden' : 'visible';

    const pinIn = smooth(progress(t, .85, 1.16));
    state.vachana.style.opacity = String(pinIn * (1 - smooth(progress(t, 3.65, 4.1))));
    state.yash.style.opacity = String(smooth(progress(t, 1.04, 1.30)) * (1 - smooth(progress(t, 4.05, 4.6))));
    const lineP = smooth(progress(t, 1.02, 1.8));
    state.reveal.style.strokeDashoffset = String(state.routeLength * (1 - lineP));
    const routeOpacity = String(pinIn * (1 - smooth(progress(t, 3.65, 4.15))));
    state.route.style.opacity = routeOpacity;
    state.routeUnder.style.opacity = routeOpacity;
    state.distance.style.opacity = String(smooth(progress(t, 1.18, 1.40)) * (1 - smooth(progress(t, 3.82, 4.10))));
    state.distance.style.transform = `translateY(${(16 * (1 - smooth(progress(t, 1.18, 1.40)))).toFixed(1)}px)`;

    // Yash's live clip fades in under the end of the zoom: opacity only, no scale (no secondary push).
    const reveal = smooth(progress(t, 4.02, 5));
    state.yashImage.style.opacity = String(reveal);
    state.yashImage.style.transform = 'none';
    state.yashImage.style.visibility = t <= 4.02 ? 'hidden' : 'visible';
    state.yashImage.style.clipPath = 'none';
  }
  global.Overhead = { mount, render };
})(window);
