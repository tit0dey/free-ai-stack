# TITONOMICS — code-only short pipeline

No stock footage. Every frame is drawn with Pillow; audio bed is synthesised with numpy;
mux with ffmpeg. 1080x1920 / 30 fps / H.264 High / AAC 192k 48 kHz.

    python3 audio_bed.py          # build/bed.wav (drone, pulse, whooshes, impacts, risers, VO ducking)
    python3 render.py             # build/video_silent.mp4 (900 frames @ 30fps)
    python3 render.py --preview 1.2 8.6   # inspect stills

Mix + master:

    ffmpeg -i build/bed.wav -i ../assets/voiceover_shein.mp3 \
      -filter_complex "[1:a]aresample=48000[vo];[0:a][vo]amix=inputs=2:duration=longest:normalize=0,\
    alimiter=limit=0.95,loudnorm=I=-14:TP=-1:LRA=9" -ar 48000 -ac 2 build/mix.wav

Output: `TITONOMICS_SHEIN_short.mp4` — 30.0 s, 1080x1920, 30 fps, ~10.4 Mbps, -14.5 LUFS, TP -3.9 dBFS.

Assets: `assets/voiceover_shein.mp3` (TTS narration), `assets/mascot_chibi.png` (chibi detective, keyed to `build/mascot_rgba.png`).
