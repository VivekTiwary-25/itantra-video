/* Scene 2 sonar campus renderer (Three.js r160, global build). Deterministic: every frame is a pure function of
 * time, so HyperFrames can seek to any frame. Geometry comes from geo.js (window.GEO), which build.py writes from
 * film/scene2/geo/campus_outlines.json (traced) and nie_north_osm.json (roads).
 *
 * World units = pixels of the stitched z18 image (about 0.58 m). x = px - CX (east), z = py - CZ (south), y = up.
 */
(function () {
  'use strict';
  const T = window.THREE;
  const CX = 470, CZ = 640;
  const MAXP = 6;

  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const wx = p => p[0] - CX, wz = p => p[1] - CZ;

  function inPoly(x, y, pts) {
    let c = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const [xi, yi] = pts[i], [xj, yj] = pts[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  }

  const COMMON = `
    uniform float uTime, uFade, uFloor, uFogNear, uFogFar;
    uniform vec4 uP[${MAXP}];
    uniform int uN;
    float hash(float n) { return fract(sin(n) * 43758.5453123); }
    // hot: flash as a pulse front passes; rev: how far this spot has been revealed (stays, so the campus remains visible)
    void pulse(vec3 pos, out float hot, out float rev) {
      hot = 0.0; rev = 0.0;
      for (int i = 0; i < ${MAXP}; i++) {
        if (i >= uN) break;
        vec4 p = uP[i];
        float d = length(vec3(pos.x - p.x, pos.y, pos.z - p.y));
        float dt = uTime - (p.z + d / p.w);
        if (dt > 0.0) { hot = max(hot, exp(-dt * 2.4)); rev = max(rev, 1.0 - exp(-dt * 1.6)); }
        else { hot = max(hot, exp(dt * 16.0) * 0.3); }
      }
    }
    float fog(float z) { return clamp(1.0 - (z - uFogNear) / (uFogFar - uFogNear), 0.18, 1.0); }
  `;

  const PTS_VS = COMMON + `
    uniform float uScale;
    attribute float aB; attribute float aR; attribute float aK;
    varying float vI; varying float vHot; varying float vK;
    void main() {
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_Position = projectionMatrix * mv;
      float hot, rev; pulse(position, hot, rev);
      float fl = hash(aR * 113.1 + floor(uTime * 7.0 + aR * 11.0));
      float flick = mix(1.0, 0.45 + 1.1 * fl, 0.4);            // intermittent light
      vI = aB * (uFloor * rev * flick + hot * (0.55 + 0.45 * aB)) * uFade * fog(-mv.z);
      vHot = hot; vK = aK;
      gl_PointSize = clamp(uScale * (0.75 + 0.5 * aB) * (1.0 + 0.6 * hot) / -mv.z, 1.0, 9.0);
    }`;
  const PTS_FS = `
    uniform vec3 uCold, uHot, uGround;
    varying float vI; varying float vHot; varying float vK;
    void main() {
      vec2 c = gl_PointCoord - 0.5; float r = length(c);
      if (r > 0.5) discard;
      float a = smoothstep(0.5, 0.05, r);
      vec3 base = vK < 0.5 ? uGround : uCold;
      vec3 col = mix(base, uHot, clamp(vHot * 1.2, 0.0, 1.0));
      gl_FragColor = vec4(col * vI * a, 1.0);
    }`;
  const LIN_VS = COMMON + `
    attribute float aB;
    varying float vI; varying float vHot;
    void main() {
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_Position = projectionMatrix * mv;
      float hot, rev; pulse(position, hot, rev);
      vI = aB * (uFloor * rev + hot) * uFade * fog(-mv.z);
      vHot = hot;
    }`;
  const LIN_FS = `
    uniform vec3 uCold, uHot;
    varying float vI; varying float vHot;
    void main() { gl_FragColor = vec4(mix(uCold, uHot, clamp(vHot, 0.0, 1.0)) * vI, 1.0); }`;
  const RING_VS = `
    varying vec3 vW;
    void main() { vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
  const RING_FS = `
    uniform float uTime, uFade, uRingFade;
    uniform vec4 uP[${MAXP}];
    uniform int uN;
    uniform vec3 uCol;
    varying vec3 vW;
    void main() {
      float v = 0.0;
      for (int i = 0; i < ${MAXP}; i++) {
        if (i >= uN) break;
        vec4 p = uP[i];
        float age = uTime - p.z;
        if (age <= 0.0) continue;
        float r = age * p.w, d = length(vW.xz - p.xy);
        float fade = exp(-age * 0.5) * smoothstep(0.0, 0.2, age);
        float front = exp(-pow((d - r) / 1.6, 2.0)) * 0.5;
        float wake = d < r ? exp(-(r - d) / 22.0) * 0.07 : 0.0;
        v += (front + wake) * fade;
      }
      float edge = exp(-pow(length(vW.xz) / 820.0, 2.0));
      gl_FragColor = vec4(uCol * v * edge * uFade * uRingFade, 1.0);
    }`;

  function Sonar(canvas, geo) {
    const R = rng(20260930);
    const renderer = new T.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
    renderer.setPixelRatio(1);
    renderer.setSize(1920, 1080, false);
    renderer.setClearColor(0x000000, 1);
    const scene = new T.Scene();
    const cam = new T.PerspectiveCamera(30, 1920 / 1080, 5, 6000);

    const uniforms = {
      uTime: { value: 0 }, uFade: { value: 1 }, uRingFade: { value: 1 }, uFloor: { value: 0.34 },
      uFogNear: { value: 400 }, uFogFar: { value: 1500 },
      uP: { value: Array.from({ length: MAXP }, () => new T.Vector4(0, 0, 1e6, 1)) }, uN: { value: 0 },
      uScale: { value: 2100 },
      uCold: { value: new T.Color('#b4d6f4') }, uHot: { value: new T.Color('#f2f9ff') }, uGround: { value: new T.Color('#7aa2c6') },
      uCol: { value: new T.Color('#7fb4de') },
    };

    // ---------------------------------------------------------------- points
    const P = [], B = [], RR = [], K = [];
    const add = (x, y, z, b, k) => { P.push(x, y, z); B.push(b); RR.push(R()); K.push(k); };
    const jit = s => (R() - 0.5) * s;

    function walls(pts, h, dens, bright, closed = true) {
      const n = pts.length;
      for (let i = 0; i < (closed ? n : n - 1); i++) {
        const a = pts[i], b = pts[(i + 1) % n];
        const L = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const steps = Math.max(2, Math.ceil(L / 1.1));
        for (let s = 0; s < steps; s++) {
          const f = s / steps, x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
          add(wx([x, y]) + jit(0.3), h, wz([x, y]) + jit(0.3), bright, 1);            // roof edge
          if (R() < 0.7) add(wx([x, y]) + jit(0.3), 0.2, wz([x, y]) + jit(0.3), bright * 0.55, 1);   // base
          for (let yy = 2.2; yy < h - 1; yy += 2.6) {                                   // wall grain (floors)
            if (R() < dens) add(wx([x, y]) + jit(0.5), yy + jit(0.6), wz([x, y]) + jit(0.5), bright * (0.35 + 0.3 * R()), 1);
          }
        }
        for (let yy = 0; yy < h; yy += 0.9) add(wx(a) + jit(0.2), yy, wz(a) + jit(0.2), bright * 0.9, 1);   // corner
      }
    }
    function roof(pts, h, per, bright) {
      const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
      const n = Math.round((x1 - x0) * (y1 - y0) / per);
      for (let i = 0; i < n; i++) {
        const x = x0 + R() * (x1 - x0), y = y0 + R() * (y1 - y0);
        if (inPoly(x, y, pts)) add(wx([x, y]), h, wz([x, y]), bright * (0.5 + 0.5 * R()), 1);
      }
    }
    for (const b of geo.campus) {
      walls(b.pts, b.h, 0.5, 1.0);
      roof(b.pts, b.h, b.court ? 22 : 16, 0.32);
      if (b.court) walls(b.court, b.h, 0.35, 0.8);
    }
    for (const b of geo.context) { walls(b.pts, b.h, 0.14, 0.26); roof(b.pts, b.h, 70, 0.12); }

    // sports ground (superellipse), pitch and court: flat
    const ov = geo.oval;
    const ovalPts = (dr) => {
      const out = [];
      for (let i = 0; i < 720; i++) {
        const a = 2 * Math.PI * i / 720, c = Math.cos(a), s = Math.sin(a);
        out.push([ov.center[0] + (ov.rx + dr) * Math.sign(c) * Math.pow(Math.abs(c), 2 / ov.n),
                  ov.center[1] + (ov.ry + dr) * Math.sign(s) * Math.pow(Math.abs(s), 2 / ov.n)]);
      }
      return out;
    };
    for (const p of ovalPts(0)) add(wx(p) + jit(0.4), 0.3, wz(p) + jit(0.4), 0.85, 1);
    for (const p of ovalPts(-7)) if (R() < 0.6) add(wx(p) + jit(0.4), 0.3, wz(p) + jit(0.4), 0.45, 1);
    for (let i = 0; i < 1400; i++) {
      const x = ov.center[0] + (R() * 2 - 1) * ov.rx, y = ov.center[1] + (R() * 2 - 1) * ov.ry;
      if (Math.pow(Math.abs((x - ov.center[0]) / ov.rx), ov.n) + Math.pow(Math.abs((y - ov.center[1]) / ov.ry), ov.n) < 1)
        add(wx([x, y]), 0.2, wz([x, y]), 0.14, 0);
    }
    for (const r of geo.rects) walls(r.pts, 0.4, 0, 0.5);

    // roads: two edge rows plus a faint centre
    for (const rd of geo.roads) {
      const half = rd.w / 2;
      for (let i = 0; i < rd.pts.length - 1; i++) {
        const a = rd.pts[i], b = rd.pts[i + 1];
        const L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L < 0.01) continue;
        const nx = -(b[1] - a[1]) / L, ny = (b[0] - a[0]) / L;
        for (let s = 0; s < L; s += 1.3) {
          const x = a[0] + (b[0] - a[0]) * s / L, y = a[1] + (b[1] - a[1]) * s / L;
          for (const side of [-1, 1]) add(wx([x + nx * half * side, y + ny * half * side]) + jit(0.6), 0.1, wz([x + nx * half * side, y + ny * half * side]) + jit(0.6), rd.b, 0);
          if (R() < 0.25) add(wx([x, y]) + jit(half), 0.1, wz([x, y]) + jit(half), rd.b * 0.5, 0);
        }
      }
    }
    // ground grain: sparse returns, thinning out away from the campus
    for (let i = 0; i < 26000; i++) {
      const x = R() * 1547, y = R() * 1260;
      const d = Math.hypot(x - 470, y - 640);
      if (R() > Math.exp(-(d * d) / (2 * 560 * 560))) continue;
      add(wx([x, y]), 0, wz([x, y]), 0.16 + 0.26 * R(), 0);
    }
    const pg = new T.BufferGeometry();
    pg.setAttribute('position', new T.Float32BufferAttribute(P, 3));
    pg.setAttribute('aB', new T.Float32BufferAttribute(B, 1));
    pg.setAttribute('aR', new T.Float32BufferAttribute(RR, 1));
    pg.setAttribute('aK', new T.Float32BufferAttribute(K, 1));
    const pm = new T.ShaderMaterial({ uniforms, vertexShader: PTS_VS, fragmentShader: PTS_FS,
      blending: T.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true });
    scene.add(new T.Points(pg, pm));

    // ---------------------------------------------------------------- outlines
    const LP = [], LB = [];
    const seg = (a, ha, b, hb, br) => { LP.push(wx(a), ha, wz(a), wx(b), hb, wz(b)); LB.push(br, br); };
    function box(pts, h, br) {
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i], b = pts[(i + 1) % pts.length];
        seg(a, h, b, h, br); seg(a, 0.2, b, 0.2, br * 0.45); seg(a, 0, a, h, br * 0.6);
      }
    }
    for (const b of geo.campus) { box(b.pts, b.h, 0.55); if (b.court) box(b.court, b.h, 0.35); }
    for (const b of geo.context) for (let i = 0; i < b.pts.length; i++) seg(b.pts[i], b.h, b.pts[(i + 1) % b.pts.length], b.h, 0.09);
    const o0 = ovalPts(0);
    for (let i = 0; i < o0.length; i += 4) seg(o0[i], 0.3, o0[(i + 4) % o0.length], 0.3, 0.35);
    const lg = new T.BufferGeometry();
    lg.setAttribute('position', new T.Float32BufferAttribute(LP, 3));
    lg.setAttribute('aB', new T.Float32BufferAttribute(LB, 1));
    const lm = new T.ShaderMaterial({ uniforms, vertexShader: LIN_VS, fragmentShader: LIN_FS,
      blending: T.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true });
    scene.add(new T.LineSegments(lg, lm));

    // ---------------------------------------------------------------- pulse rings on the ground
    const rg = new T.PlaneGeometry(2400, 2400, 1, 1); rg.rotateX(-Math.PI / 2);
    const rm = new T.ShaderMaterial({ uniforms, vertexShader: RING_VS, fragmentShader: RING_FS,
      blending: T.AdditiveBlending, depthWrite: false, depthTest: false, transparent: true });
    const ring = new T.Mesh(rg, rm); ring.renderOrder = -1; scene.add(ring);

    // ---------------------------------------------------------------- API
    const v3 = new T.Vector3();
    function setCam(c) {
      const ph = c.pitch * Math.PI / 180, th = (c.yaw || 0) * Math.PI / 180;
      const tx = c.tx - CX, tz = c.tz - CZ;
      cam.position.set(tx + c.D * Math.cos(ph) * Math.sin(th), c.D * Math.sin(ph), tz + c.D * Math.cos(ph) * Math.cos(th));
      cam.up.set(0, 1, 0);
      cam.lookAt(tx, 0, tz);
      cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    }
    function project(px, py, h) {
      v3.set(px - CX, h || 0, py - CZ).project(cam);
      return { x: (v3.x + 1) * 960, y: (1 - v3.y) * 540, ok: v3.z < 1 };
    }
    // pulses: [{x, y (map px), t0, speed}]
    function render(t, o) {
      uniforms.uTime.value = t;
      uniforms.uFade.value = o.fade == null ? 1 : o.fade;
      uniforms.uFloor.value = o.floor == null ? 0.34 : o.floor;
      uniforms.uRingFade.value = o.ringFade == null ? 1 : o.ringFade;
      const ps = o.pulses || [];
      uniforms.uN.value = Math.min(ps.length, MAXP);
      ps.slice(0, MAXP).forEach((p, i) => uniforms.uP.value[i].set(p.x - CX, p.y - CZ, p.t0, p.speed));
      setCam(o.cam);
      const d = o.cam.D;
      uniforms.uFogNear.value = d * 0.55; uniforms.uFogFar.value = d * 2.4;
      uniforms.uScale.value = 2100 * (o.pointScale || 1) * (d / 900);
      renderer.render(scene, cam);
    }
    return { render, project, setCam, camera: cam };
  }

  // ---------------------------------------------------------------- small helpers shared by the pages
  const clamp01 = x => Math.max(0, Math.min(1, x));
  const ease = {
    lin: x => clamp01(x),
    inOut: x => { x = clamp01(x); return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; },
    sine: x => { x = clamp01(x); return -(Math.cos(Math.PI * x) - 1) / 2; },
    out: x => { x = clamp01(x); return 1 - Math.pow(1 - x, 3); },
    in: x => { x = clamp01(x); return x * x * x; },
    outQuart: x => { x = clamp01(x); return 1 - Math.pow(1 - x, 4); },
  };
  const span = (t, a, b) => (t - a) / (b - a);
  const lerp = (a, b, f) => a + (b - a) * f;
  function lerpCam(a, b, f, fD) {
    return { tx: lerp(a.tx, b.tx, f), tz: lerp(a.tz, b.tz, f), pitch: lerp(a.pitch, b.pitch, f), yaw: lerp(a.yaw || 0, b.yaw || 0, f),
             D: Math.exp(lerp(Math.log(a.D), Math.log(b.D), fD == null ? f : fD)) };
  }

  window.Sonar = Sonar;
  window.SonarUtil = { ease, span, lerp, lerpCam, clamp01 };
})();
