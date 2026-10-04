---
status: done
---
# R0004 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
=== done 2026-10-04T11:59:45
=== 2026-10-04T12:10:16 commit 80e308e5 segs exploded
--- exploded start 12:10:16: film\exploded_v2\render.cmd
--- exploded exit 1 after 1 s
=== done 2026-10-04T12:10:18
```

(check: no segment reported exit 0)

## Assembly (draft), exit 0
```
.57-38.77 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 117.77-118.67 s = s3 40.07-40.97 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 118.67-119.80 s = s3 40.97-42.10 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 124.87-126.20 s = s3 47.17-48.50 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 126.33-126.87 s = s3 48.63-49.17 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 127.47-128.03 s = s3 49.77-50.33 s"                 live camera never freezes: check this hold
INFO    freeze >= 0.5 s in exploded (slate) "film 129.10-131.10 s = exploded 0.00-2.00 s"             graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 133.53-134.90 s = cards 2.43-3.80 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 134.90-136.23 s = cards 3.80-5.13 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 136.23-137.57 s = cards 5.13-6.47 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 137.57-138.90 s = cards 6.47-7.80 s"                graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.35                                                    -16 +/-1 LUFS
INFO    true peak                      -1.62                                                     <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -19.7 /  -21.0 /  -12.7
    10-20    -17.7 /  -21.2 /  -10.0
    20-30    -18.6 /  -21.9 /  -13.3
    30-40    -19.8 /  -22.4 /  -14.4
    40-50    -14.8 /  -20.0 /  -12.2
    50-60    -24.5 /  -26.7 /  -12.3
    60-70    -24.4 /  -26.0 /  -21.6
    70-80    -22.7 /  -26.7 /  -15.8
    80-90    -13.4 /  -17.6 /  -12.3
    90-100   -19.5 /  -25.5 /  -14.1
   100-110   -14.3 /  -26.5 /  -12.5
   110-120   -18.2 /  -23.9 /  -12.9
   120-130   -13.9 /  -20.5 /  -11.5
   130-140   -19.4 /  -21.2 /  -17.3
   140-150   -17.0 /  -18.8 /  -16.6
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_draft_qc.json
WARNING: intro: RENDERS:intro_v3/intro_v3.mp4 missing; using a 2 s slate
WARNING: exploded: RENDERS:exploded_v2/exploded_v2.mp4 missing; using a 2 s slate
intro     start    0.000    2.000 s     60 frames  [SLATE]
s2a       start    2.000   43.300 s   1299 frames
s2b       start   45.300   32.400 s    972 frames
s3        start   77.700   51.400 s   1542 frames
exploded  start  129.100    2.000 s     60 frames  [SLATE]
cards     start  131.100   14.000 s    420 frames
film: 145.100 s, 4353 frames
WARNING: music: 2 short section(s) merged for the bed (anything under 6 s)
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3_draft.mp4  145.100 s, -16.35 LUFS, -1.62 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_draft_report.json  (3 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_draft_qc.json)
```
