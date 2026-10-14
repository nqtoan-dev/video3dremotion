@echo off
title video3dremotion — DCI 2K Cinema Studio
echo ============================================================================
echo   KHOI DONG VIDEO3DREMOTION STUDIO (DCI 2K 2048x1080 @ 24FPS)
echo   Toi uu cho Dell Precision 7530 (Xeon E-2176M + NVIDIA Quadro P2000 4GB)
echo ============================================================================

if not exist "luts\kodak_2383_cinema.cube" (
    python scripts\generate_kodak2383_lut.py
)

start "" "studio_ui\video3dremotion_studio.html"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
