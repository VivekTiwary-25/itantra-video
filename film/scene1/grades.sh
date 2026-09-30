# Scene 1 colour: part-2-to-part-1 match plus three look options (source this file).
MATCH2="lutrgb=r='clip(val*0.970,0,255)':g='clip(val*0.972,0,255)':b='clip(val*0.966,0,255)'"
# A: warm cinematic - warm mids/highlights, teal-leaning shadows, soft S-curve with highlight roll-off, vignette
GRADE_A="curves=master='0/0.03 0.15/0.12 0.5/0.51 0.85/0.87 1/0.95',colorbalance=rs=-0.05:bs=0.07:rm=0.07:gm=0.01:bm=-0.06:rh=0.06:gh=0.02:bh=-0.06,eq=saturation=0.96,vignette=a=PI/5"
# B: punchy contrast - deep S-curve, richer colour, a little extra crispness
GRADE_B="curves=master='0/0 0.2/0.12 0.5/0.5 0.8/0.88 1/0.97',eq=saturation=1.14,unsharp=5:5:0.5:5:5:0,vignette=a=PI/6"
# C: cool / muted - lifted blacks, cooler balance, much lower saturation
GRADE_C="curves=master='0/0.07 0.5/0.49 1/0.93',colorbalance=rs=-0.03:gs=0.01:bs=0.05:rm=-0.03:bm=0.04:rh=-0.02:bh=0.03,eq=saturation=0.7,vignette=a=PI/6"
