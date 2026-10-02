---
status: done
---

# T0044 phone screen re-record kit

Made `film/intro30/screen/record.py` and `film/intro30/screen/taps.json`. The script starts a silent scrcpy MKV at the phone's native resolution, capped at 2400 pixels on its long side (the earlier captures were 1080×2400). It schedules ADB gestures from the timing file and writes a matching `.log` with planned and measured times. It stops the screen capture 0.5 seconds before the scheduled PTT release, then lets the ADB hold finish. No phone was connected or changed for this task.

## Steps for Vivek

1. Put `scrcpy.exe` and `adb.exe` in `local/tools/` or `local/tools/scrcpy/`, or make them available on PATH. They were not present in this worker clone when checked.
2. Review the over-shoulder take frame by frame. Edit `film/intro30/screen/taps.json`: replace **all** example times with seconds from the start of that take; replace the zero `x`/`y` coordinates for Airplane Mode, the iTantra icon, and PTT with coordinates from this phone's 1080×2400 screen. Adjust swipe coordinates if the Quick Settings layout differs. Keep `ptt_up` after `ptt_down`; the script stops recording before `ptt_up` so the baked-in transcription is never shown.
3. On the phone, enable USB debugging and authorize this PC. Unlock it manually; leave it on the home screen with iTantra's icon visible and Airplane Mode initially off. Do not start the phone's screen recorder. The script does not unlock the phone.
4. Preview the schedule without a phone: `python film/intro30/screen/record.py --dry-run`. Check that the printed actions and stop time match the take.
5. With the phone attached, run `python film/intro30/screen/record.py`. The MKV and log are written under `RENDERS:intro30/screen/` as matching `screen-YYYYMMDD-HHMMSS.mkv` and `.log` files. Review the result at the PTT end and align the real tap times in the log against the over-shoulder footage. If the release or baked transcription is visible, increase `cut_before_release_ms` and record again.

Validation: `python film/intro30/screen/record.py --dry-run` completed without a phone and printed all ADB commands, the stop time, and a warning to replace placeholder coordinates. An actual capture was not attempted because the task forbids connecting to or changing a phone.
