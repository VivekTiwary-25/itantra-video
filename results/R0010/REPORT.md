---
status: done
---
# R0010 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
--- intro start 17:34:16: film\intro_v3\render.cmd
--- intro exit 0 after 650 s
=== done 2026-10-04T17:45:06
=== 2026-10-04T17:46:21 commit 99b512aa segs s3 s4 cards
--- s3 start 17:46:21: python film\scene3\v3\build.py
--- s3 exit 1 after 0 s
--- s4 start 17:46:21: film\scene4\render.cmd
--- s4 exit 0 after 150 s
--- cards start 17:48:51: python film\cards_v3\cards_sfx.py && film\cards_v3\render.cmd
--- cards exit 0 after 78 s
=== done 2026-10-04T17:50:09
```

## Assembly (draft), exit 0
```
7-193.77 s = s4 15.27-15.77 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s4          "film 194.77-195.37 s = s4 16.77-17.37 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s4          "film 196.67-197.47 s = s4 18.67-19.47 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s4          "film 197.47-198.03 s = s4 19.47-20.03 s"                 live camera never freezes: check this hold
INFO    freeze >= 0.5 s in cards       "film 200.73-202.07 s = cards 2.43-3.77 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 202.07-203.43 s = cards 3.77-5.13 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 203.43-204.70 s = cards 5.13-6.40 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 204.70-206.03 s = cards 6.40-7.73 s"                graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.26                                                    -16 +/-1 LUFS
INFO    true peak                      -1.63                                                     <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -12.5 /  -14.0 /  -11.5
    10-20    -12.3 /  -13.8 /  -11.4
    20-30    -12.1 /  -14.5 /  -10.7
    30-40    -17.6 /  -27.1 /  -11.8
    40-50    -23.1 /  -27.8 /  -11.6
    50-60    -22.1 /  -27.0 /  -16.5
    60-70    -17.1 /  -27.8 /  -12.8
    70-80    -26.0 /  -29.3 /  -12.4
    80-90    -33.1 /  -38.9 /  -27.0
    90-100   -37.3 /  -38.9 /  -36.8
   100-110   -32.0 /  -38.1 /  -28.7
   110-120   -29.7 /  -32.2 /  -27.2
   120-130   -27.5 /  -30.5 /  -17.4
   130-140   -15.8 /  -22.4 /  -14.6
   140-150   -23.9 /  -29.3 /  -14.5
   150-160   -20.5 /  -31.7 /  -14.5
   160-170   -22.5 /  -25.9 /  -14.5
   170-180   -16.6 /  -26.6 /  -13.5
   180-190   -26.5 /  -29.2 /  -24.2
   190-200   -26.2 /  -28.7 /  -23.8
   200-210   -23.1 /  -24.6 /  -20.5
   210-220   -22.4 /  -24.7 /  -20.7
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_draft_qc.json
WARNING: intro: no expected_duration in the segments file; accepted 33.600 s
WARNING: s2a: no expected_duration in the segments file; accepted 41.100 s
WARNING: s2b: no expected_duration in the segments file; accepted 51.900 s
WARNING: s3: no expected_duration in the segments file; accepted 51.400 s
WARNING: s4: no expected_duration in the segments file; accepted 20.300 s
intro     start    0.000   33.600 s   1008 frames
s2a       start   33.600   41.100 s   1233 frames
s2b       start   74.700   51.900 s   1557 frames
s3        start  126.600   51.400 s   1542 frames
s4        start  178.000   20.300 s    609 frames
cards     start  198.300   14.000 s    420 frames
film: 212.300 s, 6369 frames
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3_draft.mp4  212.300 s, -16.26 LUFS, -1.63 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_draft_report.json  (5 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_draft_qc.json)
```
