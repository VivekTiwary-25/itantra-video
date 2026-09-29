---
status: done
---

Created a 1920x1080, three-second iTantra title composition with local GSAP and two preview PNGs.

Commands run (with `HYPERFRAMES_NO_TELEMETRY=1` and `HYPERFRAMES_SKIP_SKILLS=1`):

- `hyperframes.cmd init project --non-interactive --skip-transcribe`
- `hyperframes.cmd check` - passed: 0 lint, runtime, and motion errors; 0 layout issues.
- `hyperframes.cmd snapshot --at 0.2,1.5 --no-end -o snaps`

`preview/snapshot-0.2s.png` shows only the dark background. `preview/snapshot-1.5s.png` shows the centred, near-white "iTantra" title. The temporary `snaps` folder was removed.
