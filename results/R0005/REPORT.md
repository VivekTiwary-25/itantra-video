---
status: done
---
# R0005 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
=== done 2026-10-04T12:10:18
=== 2026-10-04T12:25:29 commit 1f7e5513 segs intro
--- intro start 12:25:29: film\intro_v3\render.cmd
--- intro exit 0 after 55 s
=== done 2026-10-04T12:26:25
```

## Assembly (draft), exit 0
```
ck this hold
REVIEW  freeze >= 0.5 s in s3          "film 117.77-118.67 s = s3 40.07-40.97 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 118.67-119.80 s = s3 40.97-42.10 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 124.87-126.20 s = s3 47.17-48.50 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 126.33-126.87 s = s3 48.63-49.17 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 127.47-128.03 s = s3 49.77-50.33 s"                 live camera never freezes: check this hold
INFO    freeze >= 0.5 s in exploded    "film 129.10-129.83 s = exploded 0.00-0.73 s"             graphic hold, allowed
INFO    freeze >= 0.5 s in exploded    "film 144.43-145.10 s = exploded 15.33-16.00 s"           graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 147.53-148.90 s = cards 2.43-3.80 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 148.90-150.23 s = cards 3.80-5.13 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 150.23-151.57 s = cards 5.13-6.47 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 151.57-152.90 s = cards 6.47-7.80 s"                graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.4                                                     -16 +/-1 LUFS
INFO    true peak                      -1.63                                                     <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -19.4 /  -20.7 /  -12.6
    10-20    -17.4 /  -20.9 /   -9.9
    20-30    -18.4 /  -21.6 /  -13.2
    30-40    -19.5 /  -22.1 /  -14.2
    40-50    -14.6 /  -19.7 /  -12.1
    50-60    -24.2 /  -26.4 /  -12.2
    60-70    -24.1 /  -25.7 /  -21.3
    70-80    -22.4 /  -26.4 /  -15.6
    80-90    -13.2 /  -17.3 /  -12.0
    90-100   -19.3 /  -25.3 /  -13.9
   100-110   -14.1 /  -26.2 /  -12.3
   110-120   -18.0 /  -23.7 /  -12.7
   120-130   -13.7 /  -20.2 /  -11.3
   130-140   -19.5 /  -21.8 /  -19.2
   140-150   -19.3 /  -19.7 /  -18.9
   150-160   -17.4 /  -19.4 /  -15.8
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_draft_qc.json
WARNING: intro: RENDERS:intro_v3/intro_v3.mp4 missing; using a 2 s slate
intro     start    0.000    2.000 s     60 frames  [SLATE]
s2a       start    2.000   43.300 s   1299 frames
s2b       start   45.300   32.400 s    972 frames
s3        start   77.700   51.400 s   1542 frames
exploded  start  129.100   16.000 s    480 frames
cards     start  145.100   14.000 s    420 frames
film: 159.100 s, 4773 frames
WARNING: music: 1 short section(s) merged for the bed (anything under 6 s)
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3_draft.mp4  159.100 s, -16.4 LUFS, -1.63 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_draft_report.json  (2 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_draft_qc.json)
```
