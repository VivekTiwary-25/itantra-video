# iTantra v3 glass kit

Use `glass.css` on a 1920 × 1080 composition and load `glass.js` when the phone, icons, or strike animation are needed. This kit has no network dependencies.

## Build-time copy

Copy the three runtime files `film/common/glass/{glass.css,glass.js,noise.png}` into the composition's `assets/glass/` before running HyperFrames. Link `<link rel="stylesheet" href="assets/glass/glass.css">` and `<script src="assets/glass/glass.js"></script>`. Keep `noise.png` beside `glass.css`; its URL is relative to the stylesheet. The demo and source scripts are reference material and are not copied into final compositions. Do not edit the shared kit inside a scene. Use local scene CSS for positioning and make style changes here only when they should affect every scene.

## Components

- `.glass-card` is the 64 px title card. Add `.full` for a 1920 × 1080, near-opaque transition sheet.
- `.glass-panel` is a smaller panel with 40 px primary and 30 px `.secondary` text.
- `.glass-circle` is light matte glass with dark content. Give it an explicit equal width and height.
- `.techline` sits at y=64 and holds one line; optional `<small>` adds a second 22 px line.
- `.caption` sits at the bottom centre with a baseline near y=1000. Keep it to two lines and move it when the phone UI needs that space.
- `.label-pin` is a 26 px map or sonar label.

Use the colour variables by meaning: `--blue` Normal, `--red` SOS, `--gold` Bluetooth glow. The phone bezel is drawn by CSS; `Glass.phone(el, {src, kind:'img'|'video'})` inserts the supplied screen media. Set `--glass-screen-height` on `el` to scale the phone (default 1000 px); the screen remains 1080:2400, has a 44 px radius at the default height, and has a 14 px bezel. Screen media must come from the real app footage or build in a film scene. `Glass.icon(name)` returns an inline SVG node for `tower`, `mobile-data`, `wifi`, `internet`, `bluetooth`, `lock`, `mic`, `speaker`, or `phone`. Append it into a sized wrapper. `Glass.cross(wrapper, progress)` draws the red-white diagonal strike from 0 to 1; call it with the current timeline value on every seek. Never strike Bluetooth.

The demo is a 4 s HyperFrames composition. Run `python film/common/glass/demo/build.py` from any clone with local footage configured in `machine.local.json`, then `hyperframes.cmd check` from `film/common/glass/demo/`. Its `assets/*.mp4` are ignored media derivatives and must never be committed. The demo's phone shows a blank colour field only so the shell can be inspected; film scenes supply the actual app screen.
