---
status: failed
---

Created `project/index.html` as a 1920×1080, three-second composition with `iTantra` centered on `#0a0a0a`. The GSAP timeline specifies a linear opacity fade from 0 at 0.3 s to 1 at 1.5 s. Both the root and text have `data-duration="3"`.

Created `preview/snapshot-1.5s.png`; it shows the title fully visible on the dark background. Removed the temporary `project/snaps` folder. No MP4 was rendered.

`hyperframes check` did **not** pass. Its first run timed out during navigation. The retry reported 0 lint errors but failed at runtime because the browser could not load `gsap@3.14.2` (`net::ERR_NETWORK_ACCESS_DENIED`); the missing GSAP timeline also caused a seek error. An attempt to obtain a local GSAP copy through npm was denied by the same machine network policy. The still alone therefore does not prove the fade works.

Commands run from `results/X004/` or its `project/` directory, with the required environment variables set for every HyperFrames command:

```powershell
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes init project --non-interactive --skip-transcribe
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes.cmd init project --non-interactive --skip-transcribe
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes.cmd check
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes.cmd check --timeout=30000
npm.cmd install --no-save --no-package-lock --ignore-scripts gsap@3.14.2
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes.cmd docs gsap
$env:HYPERFRAMES_NO_TELEMETRY='1'; $env:HYPERFRAMES_SKIP_SKILLS='1'; hyperframes.cmd snapshot --at 1.5 --no-end -o snaps
```

The first `hyperframes` invocation was blocked by PowerShell script execution policy; the `.cmd` shim initialized the project successfully.
