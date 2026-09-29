# GSAP (vendored copy)

`gsap.min.js` is GSAP 3.14.2 from https://gsap.com, copied here so HyperFrames compositions can run
without internet access (workers run in a sandbox that blocks the network, so a `<script src="https://cdn...">` fails).

GSAP is (c) GreenSock and is used under its Standard License: https://gsap.com/standard-license
Use it from a composition with a relative script tag, for example `<script src="./gsap.min.js"></script>`,
after copying this file next to the composition's `index.html`.
