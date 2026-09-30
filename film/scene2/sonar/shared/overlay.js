/* Sonar overlay: the five people points (V, R1-R3, Y), their labels, the route and the message packet.
 * Plain DOM positioned from the Three.js camera every frame, so it stays locked to the map. Deterministic. */
(function () {
  'use strict';
  const { ease, span, clamp01, lerp } = window.SonarUtil;

  function el(tag, cls, parent, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    parent.appendChild(e);
    return e;
  }

  // labels: V = "Vachana", Y = "Yash", relays = dot only
  const LABELS = { V: 'Vachana', Y: 'Yash' };
  const LABEL_SIDE = { V: 'left', Y: 'right' };

  function Overlay(root, sonar, points) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'ov-svg'); svg.setAttribute('width', 1920); svg.setAttribute('height', 1080);
    root.appendChild(svg);
    const route = document.createElementNS(svg.namespaceURI, 'path'); route.setAttribute('class', 'ov-route'); svg.appendChild(route);
    const trail = document.createElementNS(svg.namespaceURI, 'path'); trail.setAttribute('class', 'ov-trail'); svg.appendChild(trail);

    const P = {};
    for (const k of ['V', 'R1', 'R2', 'R3', 'Y']) {
      const relay = k[0] === 'R';
      const wrap = el('div', 'ov-pt ' + (relay ? 'relay' : 'person'), root);
      const beam = el('i', 'beam', wrap), ping = el('i', 'ping', wrap), halo = el('i', 'halo', wrap), core = el('i', 'core', wrap);
      let lab = null;
      if (LABELS[k]) lab = el('div', 'ov-lab ' + LABEL_SIDE[k], root, LABELS[k]);
      P[k] = { wrap, beam, ping, halo, core, lab, xy: points[k] };
    }
    const packet = el('div', 'ov-packet', root);
    const arrive = el('i', 'ov-arrive', root);

    const scr = k => sonar.project(P[k].xy[0], P[k].xy[1], 0);

    /* s = {t, on: {key: time}, labelsOn, idle (0-1), hops: [[a,b,t0,t1]], arriveAt, visible, focus: key, flare} */
    function update(s) {
      const t = s.t;
      const vis = s.visible == null ? 1 : s.visible;
      for (const k in P) {
        const p = P[k], q = scr(k), on = s.on[k];
        const a = on == null ? 1 : clamp01(span(t, on, on + 0.35));
        let bright = 1;
        // relay flashes as the packet passes through it
        for (const h of (s.hops || [])) {
          if (h[1] === k) bright += 1.4 * Math.exp(-Math.max(0, t - h[3]) * 3.5) * (t >= h[3] ? 1 : 0);
        }
        p.wrap.style.transform = `translate(${q.x.toFixed(2)}px, ${q.y.toFixed(2)}px)`;
        p.wrap.style.opacity = (a * (k === s.focus ? 1 : vis)).toFixed(3);
        const pop = on == null ? 1 : 0.4 + 0.6 * ease.out(span(t, on, on + 0.3));
        p.core.style.transform = `scale(${(pop * (1 + 0.25 * (bright - 1))).toFixed(3)})`;
        p.core.style.filter = `brightness(${bright.toFixed(3)})`;
        // ping ring when the point first lights up, and again when the packet lands on it
        let pingF = on == null ? 1 : span(t, on, on + 1.1);
        for (const h of (s.hops || [])) if (h[1] === k && t >= h[3]) pingF = span(t, h[3], h[3] + 0.9);
        const pf = clamp01(pingF);
        p.ping.style.transform = `scale(${(0.3 + 2.4 * ease.out(pf)).toFixed(3)})`;
        p.ping.style.opacity = (pf < 1 ? 0.7 * (1 - pf) : 0).toFixed(3);
        const breathe = 1 + 0.08 * Math.sin((s.idle || 0) * 2 * Math.PI / 2.6 + k.length);
        p.halo.style.transform = `scale(${breathe.toFixed(3)})`;
        const top = sonar.project(p.xy[0], p.xy[1], 34);
        const bh = Math.max(0, q.y - top.y) * ease.out(on == null ? 1 : span(t, on, on + 0.5));
        p.beam.style.height = bh.toFixed(1) + 'px';
        if (p.lab) {
          const la = clamp01(span(t, s.labelsOn == null ? -1 : s.labelsOn, (s.labelsOn == null ? -1 : s.labelsOn) + 0.5)) * vis;
          p.lab.style.opacity = la.toFixed(3);
          const dx = LABEL_SIDE[k] === 'left' ? -22 : 22;
          p.lab.style.transform = `translate(${(q.x + dx).toFixed(1)}px, ${(q.y - 2).toFixed(1)}px) translate(${LABEL_SIDE[k] === 'left' ? '-100%' : '0'}, -50%)`;
        }
      }
      // route + packet
      const hops = s.hops || [];
      let dRoute = '', dTrail = '', pk = null, pkA = 0;
      if (hops.length && t >= hops[0][2] - 0.3) { pk = scr(hops[0][0]); pkA = 1; }
      for (const [a, b, t0, t1] of hops) {
        if (t < t0) break;
        const A = scr(a), Bq = scr(b);
        const f = ease.inOut(span(t, t0, t1));
        const mid = [lerp(P[a].xy[0], P[b].xy[0], f), lerp(P[a].xy[1], P[b].xy[1], f)];
        const lift = 9 * Math.sin(Math.PI * f);
        const M = sonar.project(mid[0], mid[1], lift);
        dRoute += `M${A.x.toFixed(1)},${A.y.toFixed(1)}L${M.x.toFixed(1)},${M.y.toFixed(1)}`;
        if (t <= t1 + 0.12) {
          const f0 = ease.inOut(span(t - 0.16, t0, t1));
          const m0 = sonar.project(lerp(P[a].xy[0], P[b].xy[0], f0), lerp(P[a].xy[1], P[b].xy[1], f0), 9 * Math.sin(Math.PI * f0));
          dTrail = `M${m0.x.toFixed(1)},${m0.y.toFixed(1)}L${M.x.toFixed(1)},${M.y.toFixed(1)}`;
        }
        pk = M; pkA = 1;
      }
      route.setAttribute('d', dRoute);
      trail.setAttribute('d', dTrail);
      route.style.opacity = (0.55 * vis).toFixed(3);
      if (s.arriveAt != null && t >= s.arriveAt) {
        pkA = clamp01(1 - span(t, s.arriveAt, s.arriveAt + 0.35));
        const af = clamp01(span(t, s.arriveAt, s.arriveAt + 1.6));
        const Y = scr('Y');
        arrive.style.transform = `translate(${Y.x.toFixed(1)}px, ${Y.y.toFixed(1)}px) scale(${(0.2 + 3.2 * ease.out(af)).toFixed(3)})`;
        arrive.style.opacity = (0.85 * (1 - af)).toFixed(3);
      } else arrive.style.opacity = 0;
      if (pk) {
        const start = hops.length ? clamp01(span(t, hops[0][2] - 0.3, hops[0][2] - 0.05)) : 0;
        packet.style.transform = `translate(${pk.x.toFixed(1)}px, ${pk.y.toFixed(1)}px)`;
        packet.style.opacity = (pkA * start * vis).toFixed(3);
      } else packet.style.opacity = 0;
    }
    return { update, screen: scr };
  }
  window.SonarOverlay = Overlay;
})();
