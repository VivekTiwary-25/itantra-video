---
status: done
---
# R0012 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
--- s4 exit 0 after 150 s
--- cards start 17:48:51: python film\cards_v3\cards_sfx.py && film\cards_v3\render.cmd
--- cards exit 0 after 78 s
=== done 2026-10-04T17:50:09
=== 2026-10-04T19:44:08 commit d92c90e2 segs s2a s2b s3 s4
--- s2a start 19:44:09: node film\scene2\v3a\build.js --render
--- s2a exit 0 after 550 s
--- s2b start 19:53:19: film\scene2\v3b\render.cmd
--- s2b exit 0 after 489 s
--- s3 start 20:01:27: python film\scene3\v3\build.py
--- s3 exit 0 after 525 s
--- s4 start 20:10:12: film\scene4\render.cmd
--- s4 exit 0 after 271 s
=== done 2026-10-04T20:14:43
```

## Assembly (final), exit 0
```
k this hold
REVIEW  freeze >= 0.5 s in s3          "film 169.37-170.70 s = s3 49.77-51.10 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 170.83-173.33 s = s3 51.23-53.73 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s4          "film 176.17-176.67 s = s4 2.57-3.07 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s4          "film 176.67-177.30 s = s4 3.07-3.70 s"                   live camera never freezes: check this hold
INFO    freeze >= 0.5 s in cards       "film 190.33-191.63 s = cards 2.43-3.73 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 191.63-193.00 s = cards 3.73-5.10 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 193.00-194.37 s = cards 5.10-6.47 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 194.37-195.93 s = cards 6.47-8.03 s"                graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.2                                                     -16 +/-1 LUFS
INFO    true peak                      -1.65                                                     <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -12.6 /  -14.2 /  -11.7
    10-20    -12.5 /  -14.0 /  -11.6
    20-30    -12.3 /  -14.7 /  -10.9
    30-40    -17.8 /  -27.4 /  -12.0
    40-50    -23.4 /  -28.1 /  -11.9
    50-60    -22.5 /  -27.3 /  -17.1
    60-70    -17.4 /  -28.1 /  -13.1
    70-80    -16.9 /  -27.8 /  -12.7
    80-90    -33.4 /  -38.0 /  -15.9
    90-100   -36.6 /  -37.8 /  -31.6
   100-110   -28.7 /  -32.5 /  -27.2
   110-120   -28.4 /  -33.0 /  -17.9
   120-130   -17.9 /  -26.2 /  -14.8
   130-140   -21.6 /  -28.9 /  -14.9
   140-150   -20.2 /  -29.8 /  -14.8
   150-160   -23.5 /  -30.4 /  -14.9
   160-170   -16.1 /  -25.8 /  -13.8
   170-180   -25.0 /  -27.4 /  -15.1
   180-190   -27.8 /  -31.6 /  -23.8
   190-200   -22.8 /  -24.8 /  -21.0
   200-210   -23.0 /  -24.6 /  -21.0
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_qc.json
WARNING: intro: no expected_duration in the segments file; accepted 33.600 s
WARNING: s2a: no expected_duration in the segments file; accepted 41.100 s
WARNING: s2b: no expected_duration in the segments file; accepted 44.900 s
WARNING: s3: no expected_duration in the segments file; accepted 54.000 s
WARNING: s4: no expected_duration in the segments file; accepted 14.300 s
intro     start    0.000   33.600 s   1008 frames
s2a       start   33.600   41.100 s   1233 frames
s2b       start   74.700   44.900 s   1347 frames
s3        start  119.600   54.000 s   1620 frames
s4        start  173.600   14.300 s    429 frames
cards     start  187.900   14.000 s    420 frames
film: 201.900 s, 6057 frames
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3.mp4  201.900 s, -16.2 LUFS, -1.65 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_report.json  (5 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_qc.json)
```
