import React from "react";
import { Composition } from "remotion";
import { CinematicMaster, CinematicMasterProps } from "./CinematicMaster";

const defaultProps: CinematicMasterProps = {
  projectTitle: "VIDEO3DREMOTION — DCI 2K CINEMA",
  enableAnamorphicBars: true,
  shots: [
    {
      shotId: "shot_01",
      durationSeconds: 4.5,
      rawVideoUrl: "",
      titleOverlay: "KHỞI NGUỒN ĐẠI NGÀN",
      focalLength: "24mm Anamorphic",
      cameraMotion: "Slow Aerial Push-In",
      particlePreset: "mist",
      narrationText: "Giữa không gian mênh mông của bình minh, mọi câu chuyện vĩ đại đều bắt đầu.",
    },
    {
      shotId: "shot_02",
      durationSeconds: 4.0,
      rawVideoUrl: "",
      titleOverlay: "CHIỀU SÂU QUANG HỌC",
      focalLength: "85mm Anamorphic Macro",
      cameraMotion: "Macro Parallax Slider",
      particlePreset: "warm_dust",
      narrationText: "Từng chi tiết nhỏ nhất đều mang trong mình hơi thở của thời gian.",
    },
  ],
};

export const RemotionRoot: React.FC = () => {
  const totalSeconds = defaultProps.shots.reduce((acc, s) => acc + s.durationSeconds, 0);
  const fps = 24;

  return (
    <Composition
      id="Video3DRemotionCinema"
      component={CinematicMaster}
      durationInFrames={Math.max(24, Math.round(totalSeconds * fps))}
      fps={fps}
      width={2048}
      height={1080}
      defaultProps={defaultProps}
    />
  );
};
