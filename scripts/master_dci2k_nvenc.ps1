param (
    [string]$InputVideo = ".\out\remotion_raw_2048x1080.mp4",
    [string]$LutFile = ".\luts\kodak_2383_cinema.cube",
    [string]$OutputVideo = ".\out\final_cinema_dci2k_24fps.mp4"
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " MASTERING PHIM CHUẨN RẠP DCI 2K (2048x1080 @ 24fps) - NVENC" -ForegroundColor Cyan
Write-Host " GPU: NVIDIA Quadro P2000 (4GB) | CPU: Intel Xeon E-2176M" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

if (-not (Test-Path $LutFile)) {
    python .\scripts\generate_kodak2383_lut.py
}

ffmpeg -y -hwaccel cuda -i $InputVideo `
    -vf "scale=2048:1080:flags=lanczos,cas=0.4,lut3d=file='$LutFile',noise=c0s=4:c0f=t+u" `
    -r 24 `
    -c:v h264_nvenc `
    -preset p6 `
    -tune hq `
    -rc vbr `
    -cq 17 `
    -b:v 25M `
    -maxrate 35M `
    -bufsize 50M `
    -pix_fmt yuv420p `
    -c:a aac -b:a 320k `
    $OutputVideo

Write-Host "[HOÀN TẤT] Video DCI 2K đã xuất tại: $OutputVideo" -ForegroundColor Green
