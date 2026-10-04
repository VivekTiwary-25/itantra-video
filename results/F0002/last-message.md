F0002 is complete. The Three.js composition passes `hyperframes.cmd check`, and the two 2-second previews have identical MD5 hashes, including their one-second frames. The requested stills and previews are in [results/F0002](/<REPO>/results/F0002/REPORT.md).

The direct HyperFrames render command failed at Chrome’s startup check. HyperFrames snapshots worked, so I encoded those frames into the previews with FFmpeg. NVIDIA showed 0% use during capture; HyperFrames detected Intel graphics. The [report](/<REPO>/results/F0002/REPORT.md) records the timings and failure.

TLDR: The composition and repeatability check passed; the direct render command is blocked on this machine.