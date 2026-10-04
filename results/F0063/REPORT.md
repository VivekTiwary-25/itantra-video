---
status: done
---

## Made

- Updated `film/scene2/v3b/` so N2, N2a–N2f and N3 read their durations from `film/common/narration_v4.json` at build time. Each marked beat lasts its take plus 0.4 s. The opening map pings continue through N2a–N2e. N3 finishes before the SOS card starts.
- Covered the three relay renders' baked captions with timed soft frosted strips. Trisha, Utkarsh and Vaishnavi name pins stay above the strips.
- Rebuilt `film/captions/v3/s2b.json`, the production composition, and 13 stills at 1920 px with matching 480 px copies and `results/F0063/preview/sheet-480.jpg`. No full video render was made.

## Preview review

- `00-push`: Would a judge go “oh”? The phone handoff remains clear.
- `01-N2`: Would a judge go “oh”? The question lands as the campus sonar resolves.
- `02-N2a`: Would a judge go “oh”? The message visibly grows from Vachana's pin.
- `03-N2b`: Would a judge go “oh”? The lock and small packet make sealing clear.
- `04-N2c`: Would a judge go “oh”? The dotted relay route reads at phone size.
- `05-N2d`: Would a judge go “oh”? The wait clock and moving dot show carry time.
- `06-N2e`: Would a judge go “oh”? The six-hop claim sits beside the route.
- `07-N2f`: Would a judge go “oh”? The map hands off to a real relay person.
- `08-relay1`: Would a judge go “oh”? Trisha's pin stays visible while the caption is covered.
- `09-relay2`: Would a judge go “oh”? Utkarsh's pin stays visible while the caption is covered.
- `10-relay3`: Would a judge go “oh”? Vaishnavi's pin stays visible while the caption is covered.
- `11-N3`: Would a judge go “oh”? The arrival resolves before the mode changes.
- `12-sos`: Would a judge go “oh”? The neutral SOS card makes the change of mode clear.

## Checks and notes

- `node film/scene2/v3b/build.js --preview` and the production `node film/scene2/v3b/build.js` passed the built-in `hyperframes.cmd check`, with no missing assets. Timing assertions, preview counts, file sizes and `git diff --check` passed.
- Current duration is 41.62 s. N2f's 2.5 s beat starts the existing 18 s relay montage; the remaining relay footage continues without narration. The current manifest marks N2a–N2f as dropped, silent lines, so those beats intentionally have no narration captions.
- The relay renders retain their pre-existing camera holds; this task changes only their caption coverage and scene timing.
