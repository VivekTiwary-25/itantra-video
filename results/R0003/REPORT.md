---
status: done
---
# R0003 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
=== done 2026-10-04T11:28:20
=== 2026-10-04T11:58:44 commit 2199558d segs intro
--- intro start 11:58:45: film\intro_v3\render.cmd
--- intro exit 1 after 61 s
=== done 2026-10-04T11:59:45
```

(check: no segment reported exit 0)

## Assembly (draft), exit 0
```
               live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 113.13-114.13 s = s3 35.43-36.43 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 114.27-116.47 s = s3 36.57-38.77 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 117.77-118.67 s = s3 40.07-40.97 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 118.67-119.80 s = s3 40.97-42.10 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 124.87-126.20 s = s3 47.17-48.50 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 126.33-126.87 s = s3 48.63-49.17 s"                 live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 127.47-128.03 s = s3 49.77-50.33 s"                 live camera never freezes: check this hold
INFO    freeze >= 0.5 s in cards       "film 131.53-132.90 s = cards 2.43-3.80 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 132.90-134.23 s = cards 3.80-5.13 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 134.23-135.57 s = cards 5.13-6.47 s"                graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 135.57-136.87 s = cards 6.47-7.77 s"                graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.38                                                    -16 +/-1 LUFS
INFO    true peak                      -1.6                                                      <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -19.7 /  -21.0 /  -12.7
    10-20    -17.7 /  -21.2 /  -10.1
    20-30    -18.6 /  -21.9 /  -13.4
    30-40    -19.8 /  -22.4 /  -14.5
    40-50    -14.8 /  -20.0 /  -12.2
    50-60    -24.5 /  -26.8 /  -12.3
    60-70    -24.4 /  -26.1 /  -21.6
    70-80    -22.8 /  -26.8 /  -15.8
    80-90    -13.4 /  -17.6 /  -12.3
    90-100   -19.6 /  -25.6 /  -14.1
   100-110   -14.3 /  -26.5 /  -12.5
   110-120   -18.3 /  -24.0 /  -13.0
   120-130   -13.9 /  -20.5 /  -11.5
   130-140   -19.4 /  -22.0 /  -16.6
   140-150   -16.4 /  -20.0 /  -16.0
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_draft_qc.json
WARNING: intro: RENDERS:intro_v3/intro_v3.mp4 missing; using a 2 s slate
intro     start    0.000    2.000 s     60 frames  [SLATE]
s2a       start    2.000   43.300 s   1299 frames
s2b       start   45.300   32.400 s    972 frames
s3        start   77.700   51.400 s   1542 frames
cards     start  129.100   14.000 s    420 frames
film: 143.100 s, 4293 frames
WARNING: music: 1 short section(s) merged for the bed (anything under 6 s)
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3_draft.mp4  143.100 s, -16.38 LUFS, -1.6 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_draft_report.json  (2 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_draft_qc.json)
```
