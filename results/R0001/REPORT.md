---
status: done
---
# R0001 (render runner on vivek-pc, renders on utkarsh-pc)

## Render log
```
--- s3 start 10:46:34: python film\scene3\v3\build.py
=== 2026-10-04T10:48:58 commit 2f9167f2 segs s2a
--- s2a start 10:48:58: python film\scene2\v3a\build.py --render
--- s2a exit 1 after 498 s
=== done 2026-10-04T10:57:16
```

(check: no segment reported exit 0)

## Assembly (draft), exit 0
```
ever freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 68.33-70.40 s = s3 31.93-34.00 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 71.23-72.83 s = s3 34.83-36.43 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 72.97-75.17 s = s3 36.57-38.77 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 76.43-77.37 s = s3 40.03-40.97 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 77.37-78.53 s = s3 40.97-42.13 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 83.57-84.90 s = s3 47.17-48.50 s"                   live camera never freezes: check this hold
REVIEW  freeze >= 0.5 s in s3          "film 85.03-87.53 s = s3 48.63-51.13 s"                   live camera never freezes: check this hold
INFO    freeze >= 0.5 s in cards       "film 90.23-91.60 s = cards 2.43-3.80 s"                  graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 91.60-92.93 s = cards 3.80-5.13 s"                  graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 92.93-94.27 s = cards 5.13-6.47 s"                  graphic hold, allowed
INFO    freeze >= 0.5 s in cards       "film 94.27-95.60 s = cards 6.47-7.80 s"                  graphic hold, allowed
INFO    black frames                   []                                                        none >= 1.0 s (end fade allowed)
INFO    integrated loudness            -16.39                                                    -16 +/-1 LUFS
INFO    true peak                      -1.67                                                     <= -1.5 dBTP
INFO    full-scale samples             0                                                         0
INFO    silence > 1.5 s                []                                                        none

10 s short-term loudness (median / min / max LUFS):
     0-10    -14.7 /  -20.8 /  -12.1
    10-20    -24.2 /  -26.5 /  -14.3
    20-30    -24.6 /  -26.1 /  -22.5
    30-40    -18.9 /  -26.1 /  -14.5
    40-50    -13.2 /  -20.7 /  -12.1
    50-60    -19.6 /  -25.1 /  -12.3
    60-70    -19.0 /  -26.4 /  -12.4
    70-80    -18.1 /  -22.4 /  -12.2
    80-90    -14.7 /  -21.2 /  -11.3
    90-100   -18.4 /  -21.5 /  -16.4
   100-110   -17.1 /  -19.6 /  -16.4
JSON: D:\Presentation_Itantra\itantra-video\local\renders\full_film_v3_draft_qc.json
WARNING: intro: RENDERS:intro_v3/intro_v3.mp4 missing; using a 2 s slate
WARNING: s2a: RENDERS:scene2/v3a/scene2_picture.mp4 missing; using a 2 s slate
WARNING: s2a: dx stem RENDERS:scene2/v3a/scene2_dialogue_sfx.wav missing; silence used
intro     start    0.000    2.000 s     60 frames  [SLATE]
s2a       start    2.000    2.000 s     60 frames  [SLATE]
s2b       start    4.000   32.400 s    972 frames
s3        start   36.400   51.400 s   1542 frames
cards     start   87.800   14.000 s    420 frames
film: 101.800 s, 3054 frames
WARNING: music: 2 short section(s) merged for the bed (anything under 6 s)
music: rendering the bed (about 1.5 min for the full film)
done: RENDERS:full_film_v3_draft.mp4  101.800 s, -16.39 LUFS, -1.67 dBTP, video libx264_crf18, audio linear_gain_plus_limiter
report: RENDERS:full_film_v3_draft_report.json  (4 warning(s))
QC exit code 0 (report RENDERS:full_film_v3_draft_qc.json)
```
