# 🎬 video3dremotion — AI Director & 3D Cinematic Video-by-Code Studio (DCI 2K @ 24fps)

Hệ thống tự động hóa sản xuất video điện ảnh chuẩn rạp chiếu phim (**DCI 2K `2048x1080` / CinemaScope `2.39:1` @ `24fps`**) bằng code, kết hợp **Multi-Agent AI Filmmaking (Human-in-the-Loop)**, **Google Labs Flow (1.000 Credits Veo 3)** và **Remotion + Three.js (`@remotion/three`) + FFmpeg NVIDIA NVENC**.

Được thiết kế và tinh chỉnh phần cứng chuyên biệt cho máy trạm **Dell Precision 7530 (Intel Xeon E-2176M 6C/12T, 32GB RAM, NVIDIA Quadro P2000 4GB VRAM)**.

## ✨ Kiến Trúc Cốt Lõi (5 Tầng Tự Động Hóa & 2 Trạm Duyệt)

1. **Multi-Agent Scripting & Shot Breakdown (`backend/agents/director_graph.py`)**:
   - Bạn nhập mô tả ý tưởng video bằng tiếng Việt.
   - **Director & Screenwriter Agent** tự động lên kịch bản tổng, khóa hồ sơ nhân vật (`Character Reference Bank`) và chia nhỏ thành danh sách các cảnh quay (`Shots` dài 4–6 giây) kèm thông số máy quay (`24mm`, `35mm`, `50mm`, `85mm Anamorphic`, `f/1.8`, `Slow Dolly In`, `Tracking Shot`).
2. **Trạm Duyệt 1 — Storyboard Tĩnh Miễn Phí 0 Credit (`backend/services/google_flow_bridge.py`)**:
   - Tự động gọi Google Labs Flow tạo ảnh `First Frame` cho toàn bộ các cảnh bằng **Nano Banana 2 / Imagen 4** (**Tốn 0 Credit**).
   - Bạn xem trước trên Web Studio: cảnh nào chưa ưng bấm **Tạo lại ảnh** hoàn toàn miễn phí.
3. **Sinh Cảnh Quay Động bằng Veo 3 Fast (`Image-to-Video i2v`)**:
   - Chỉ những cảnh bạn đã bấm **Duyệt Storyboard** mới được gửi sang chế độ `i2v` của **Veo 3 Fast** (`20 credits/cảnh`) hoặc **Veo 3.1 Lite** (`10 credits/cảnh`).
4. **Trạm Duyệt 2 — Duyệt Từng Cảnh Quay Video**:
   - Xem thử từng clip cảnh quay. Nếu 1 cảnh chưa ưng, chỉ bấm quay lại đúng cảnh đó, giữ nguyên các cảnh đã đạt.
5. **Ghép Cảnh 3D, Hiệu Ứng Quang Học & Xuất Phim Chuẩn Rạp DCI 2K (`renderer/` & `scripts/`)**:
   - **Remotion + React Three Fiber (`CinematicScene3D.tsx`)**: Tạo không gian 3D có hạt bụi sáng lơ lửng (Volumetric Dust), Depth of Field (Bokeh), Motion Blur góc màn trập `180°`, chuyển cảnh âm thanh sớm **J-Cut (`0.5s`)**, chữ 3D điện ảnh và thanh chắn **CinemaScope `2.39:1`**.
   - **FFmpeg NVIDIA NVENC (`master_dci2k_nvenc.ps1`)**: Phóng nét thông minh `Lanczos + CAS (Contrast Adaptive Sharpening)`, áp bảng màu phim nhựa **3D LUT Kodak 2383 (`.cube`)** và mã hóa bằng chip phần cứng `h264_nvenc` trên card **Quadro P2000**.

## 🚀 Hướng Dẫn Cài Đặt Nhanh Trên Windows 11

### Bước 1: Cài đặt Backend Python & Cầu nối Google Labs Flow
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Cài đặt công cụ điều khiển Google Flow CLI và đăng nhập 1 lần
uv tool install gflow-cli
uv tool run --from gflow-cli playwright install chromium
gflow auth login --browser chrome

# Tạo bảng màu phim nhựa 3D LUT Kodak 2383 (.cube)
python scripts/generate_kodak2383_lut.py
```

### Bước 2: Cài đặt Engine 3D Remotion (DCI 2K)
```powershell
cd renderer
npm install
npx remotion studio
```

### Bước 3: Khởi động Server Điều Phối & Giao Diện Studio Duyệt Cảnh
```powershell
uvicorn backend.main:app --reload --port 8000
```
Mở trình duyệt tại `http://localhost:8000` (hoặc mở trực tiếp file `video3dremotion_studio.html`) để nhập ý tưởng, duyệt từng cảnh quay và xuất phim chuẩn rạp DCI 2K!
