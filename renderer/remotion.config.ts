import { Config } from "@remotion/cli/config";

// Bắt buộc dùng phần cứng GPU rời NVIDIA Quadro P2000 (4GB VRAM) qua ANGLE
Config.setChromiumOpenGlRenderer("angle");

// Khóa 3 luồng render song song: tối ưu cho Xeon E-2176M (6C/12T) + 4GB VRAM ở chuẩn DCI 2K
Config.setConcurrency(3);

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
