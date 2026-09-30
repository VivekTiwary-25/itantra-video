/* Scene 3 SOS sonar: one source (Vachana), red circular waves, Vivek's point lights red when a wave reaches it.
 * No relay chain, no packet, no relay points. Deterministic: every frame is a pure function of time.
 * Uses the scene 2 campus renderer (sonar.js, copied here) for the cold campus; the red waves are an SVG layer
 * projected onto the ground plane so they stay red while the campus keeps scene 2's cold tones. */
(function () {
  'use strict';
  const { ease: E, span, lerp, lerpCam, clamp01 } = window.SonarUtil;
  const NS = 'http://www.w3.org/2000/svg';

  function SOS(root, cfg) {
    const sonar = window.Sonar(root.querySelector('#sonar'), window.GEO);
    const svg = root.querySelector('#waves');
    const waves = cfg.waves.map(() => {
      const g = document.createElementNS(NS, 'g');
      const wake = document.createElementNS(NS, 'path'), glow = document.createElementNS(NS, 'path'), ring = document.createElementNS(NS, 'path');
      wake.setAttribute('class', 'wake'); glow.setAttribute('class', 'glow'); ring.setAttribute('class', 'ring');
      g.append(wake, glow, ring); svg.appendChild(g);
      return { g, wake, glow, ring };
    });
    const pV = root.querySelector('#pV'), pK = root.querySelector('#pK'), lV = root.querySelector('#lV'), lK = root.querySelector('#lK');
    const pingK = pK.querySelector('.ping');
    const V = cfg.V, K = cfg.VIVEK;

    function circle(r) {
      let d = '';
      for (let i = 0; i <= 120; i++) {
        const a = i * Math.PI / 60;
        const p = sonar.project(V[0] + r * Math.cos(a), V[1] + r * Math.sin(a), 0);
        d += (i ? 'L' : 'M') + p.x.toFixed(1) + ',' + p.y.toFixed(1);
      }
      return d + 'Z';
    }

    // T = sonar time (shared across the three segments); vis = overall opacity of the sonar layer
    function draw(T, cam, vis) {
      // an earlier (unseen) scan leaves the campus revealed, as at the end of scene 2; no cold ring is drawn
      sonar.render(T, { cam, pulses: [{ x: V[0], y: V[1], t0: -30, speed: 300 }], floor: 0.6, ringFade: 0 });
      const last = cfg.waves.length - 1;
      cfg.waves.forEach(([t0, rmax], i) => {
        const w = waves[i], age = T - t0, r = age * cfg.speed;
        let a = 0;
        if (age > 0) {
          a = E.sine(age / 0.25);
          a *= i === last ? 1 - E.sine(span(r, cfg.arrive_r + 8, rmax)) : 1 - E.sine(span(r, rmax * 0.5, rmax));
        }
        if (a <= 0.001) { w.g.style.opacity = 0; return; }
        const d = circle(r);
        w.ring.setAttribute('d', d); w.glow.setAttribute('d', d); w.wake.setAttribute('d', d);
        w.g.style.opacity = (a * vis).toFixed(3);
      });
      const q = sonar.project(V[0], V[1], 0), k = sonar.project(K[0], K[1], 0);
      pV.style.transform = `translate(${q.x.toFixed(1)}px, ${q.y.toFixed(1)}px)`;
      pV.style.opacity = vis.toFixed(3);
      lV.style.transform = `translate(${(q.x - 22).toFixed(1)}px, ${q.y.toFixed(1)}px) translate(-100%, -50%)`;
      lV.style.opacity = vis.toFixed(3);
      // V breathes gently with each wave it sends
      let beat = 0;
      cfg.waves.forEach(([t0]) => { const x = T - t0; if (x > -0.1 && x < 0.6) beat = Math.max(beat, Math.sin(Math.PI * clamp01((x + 0.1) / 0.7))); });
      pV.querySelector('.halo').style.transform = `scale(${(1 + 0.35 * beat).toFixed(3)})`;
      pV.querySelector('.halo').style.opacity = (0.45 + 0.4 * beat).toFixed(3);
      // Vivek: appears, lit red, as the wave reaches him
      const hit = clamp01(span(T, cfg.arrive - 0.1, cfg.arrive + 0.15));
      pK.style.transform = `translate(${k.x.toFixed(1)}px, ${k.y.toFixed(1)}px)`;
      pK.style.opacity = (hit * vis).toFixed(3);
      pK.querySelector('.core').style.transform = `scale(${(0.4 + 0.6 * E.out(hit)).toFixed(3)})`;
      const pf = clamp01(span(T, cfg.arrive, cfg.arrive + 1.0));
      pingK.style.transform = `scale(${(0.3 + 2.6 * E.out(pf)).toFixed(3)})`;
      pingK.style.opacity = (T >= cfg.arrive ? 0.8 * (1 - pf) : 0).toFixed(3);
      lK.style.transform = `translate(${(k.x + 22).toFixed(1)}px, ${k.y.toFixed(1)}px) translate(0, -50%)`;
      lK.style.opacity = (clamp01(span(T, cfg.arrive + 0.1, cfg.arrive + 0.5)) * vis).toFixed(3);
      return { V: q, K: k };
    }
    return { draw, sonar };
  }
  window.SOS = SOS;
})();
