// RGB mean absolute difference of two equal-sized 960x540 PNG stills.
const cp = require('node:child_process');
const [aPath, bPath] = process.argv.slice(2);
if (!aPath || !bPath) throw new Error('Usage: node compare.js a.png b.png');
function pixels(file) {
  return cp.execFileSync('ffmpeg', ['-v', 'error', '-i', file, '-vf', 'scale=960:540,format=rgb24', '-f', 'rawvideo', '-'], { maxBuffer: 2_000_000 });
}
const a = pixels(aPath), b = pixels(bPath);
if (a.length !== b.length) throw new Error('Pixel counts differ');
let difference = 0;
for (let i = 0; i < a.length; i++) difference += Math.abs(a[i] - b[i]);
console.log(`RGB mean absolute difference: ${(difference / a.length).toFixed(3)}/255 at 960x540`);
