#!/usr/bin/env python3
"""
Tự động sinh file màu điện ảnh 3D LUT chuẩn `.cube` (17x17x17)
mô phỏng đường cong S-Curve và tông màu Teal & Orange của phim nhựa Kodak Vision3 2383
để FFmpeg áp trực tiếp khi xuất video chuẩn rạp DCI 2K.
"""

import math
import pathlib

LUT_PATH = pathlib.Path("../luts/kodak_2383_cinema.cube")


def s_curve(x: float, contrast: float = 1.15) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 / (1.0 + math.exp(-contrast * 6.0 * (x - 0.5)))


def normalize_scurve(x: float) -> float:
    low = s_curve(0.0)
    high = s_curve(1.0)
    return (s_curve(x) - low) / (high - low)


def build_kodak_2383_lut(out_path: pathlib.Path, size: int = 17) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        'TITLE "VIDEO3DREMOTION_KODAK_2383_TEAL_ORANGE"',
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    for b_idx in range(size):
        for g_idx in range(size):
            for r_idx in range(size):
                r = r_idx / (size - 1)
                g = g_idx / (size - 1)
                b = b_idx / (size - 1)

                luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
                shadow_weight = (1.0 - luma) ** 1.5
                highlight_weight = luma ** 1.4

                r_graded = normalize_scurve(r) + 0.035 * highlight_weight - 0.025 * shadow_weight
                g_graded = normalize_scurve(g) + 0.010 * highlight_weight
                b_graded = normalize_scurve(b) + 0.040 * shadow_weight - 0.020 * highlight_weight

                r_out = max(0.0, min(1.0, r_graded))
                g_out = max(0.0, min(1.0, g_graded))
                b_out = max(0.0, min(1.0, b_graded))
                lines.append(f"{r_out:.6f} {g_out:.6f} {b_out:.6f}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  + [OK] Đã tạo file 3D LUT chuẩn rạp tại: {out_path.resolve()}")


if __name__ == "__main__":
    build_kodak_2383_lut(LUT_PATH)
