import React from "react";
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";
import { CinematicScene3D } from "./CinematicScene3D";

export interface ApprovedShot {
  shotId: string;
  durationSeconds: number;
  rawVideoUrl: string;
  voiceoverUrl?: string;
  titleOverlay?: string;
  focalLength: string;
  cameraMotion: string;
  particlePreset: string;
  narrationText?: string;
}

export interface CinematicMasterProps {
  projectTitle: string;
  shots: ApprovedShot[];
  enableAnamorphicBars: boolean;
}

const SingleCinematicShot: React.FC<{ shot: ApprovedShot }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.12], {
    extrapolateRight: "clamp",
  });

  const opacity = interpolate(
    frame,
    [0, 8, durationInFrames - 8, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const textProgress = spring({
    frame: frame - 8,
    fps,
    config: { damping: 200, stiffness: 80, mass: 1.2 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#05070a", opacity }}>
      <CameraMotionBlur shutterAngle={180} samples={6}>
        <AbsoluteFill
          style={{
            transform: `scale(${scale})`,
            filter: "contrast(1.07) saturate(1.08)",
          }}
        >
          {shot.rawVideoUrl ? (
            <OffthreadVideo
              src={shot.rawVideoUrl}
              style={{ width: "2048px", height: "1080px", objectFit: "cover" }}
            />
          ) : (
            <AbsoluteFill
              style={{
                background:
                  "radial-gradient(circle at 50% 42%, #1e293b 0%, #090d16 70%, #020408 100%)",
              }}
            />
          )}
        </AbsoluteFill>
      </CameraMotionBlur>

      <CinematicScene3D
        particlePreset={shot.particlePreset || "warm_dust"}
        cameraMotion={shot.cameraMotion}
      />

      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 56%, rgba(0,0,0,0.68) 100%)",
          pointerEvents: "none",
        }}
      />

      {shot.titleOverlay && (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              color: "#F5F2EB",
              fontSize: "52px",
              fontWeight: 300,
              letterSpacing: `${interpolate(textProgress, [0, 1], [6, 24])}px`,
              textTransform: "uppercase",
              textShadow: "0 10px 38px rgba(0, 0, 0, 0.9)",
              opacity: textProgress,
              transform: `translateY(${interpolate(textProgress, [0, 1], [22, 0])}px)`,
            }}
          >
            {shot.titleOverlay}
          </div>
        </AbsoluteFill>
      )}

      {shot.narrationText && (
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingBottom: "138px",
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              color: "#E2E8F0",
              fontSize: "26px",
              fontStyle: "italic",
              fontWeight: 400,
              maxWidth: "1360px",
              textAlign: "center",
              textShadow: "0 2px 12px rgba(0,0,0,0.95)",
              backgroundColor: "rgba(0,0,0,0.35)",
              padding: "8px 24px",
              borderRadius: "6px",
            }}
          >
            {shot.narrationText}
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

export const CinematicMaster: React.FC<CinematicMasterProps> = ({
  shots,
  enableAnamorphicBars = true,
}) => {
  const { fps } = useVideoConfig();
  const J_CUT_FRAMES = 12;

  let accumulatedFrames = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {shots.map((shot, index) => {
        const shotFrames = Math.round(shot.durationSeconds * fps);
        const startFrame = accumulatedFrames;
        accumulatedFrames += shotFrames;

        return (
          <React.Fragment key={shot.shotId}>
            <Sequence from={startFrame} durationInFrames={shotFrames}>
              <SingleCinematicShot shot={shot} />
            </Sequence>

            {shot.voiceoverUrl && (
              <Sequence
                from={Math.max(0, startFrame - (index > 0 ? J_CUT_FRAMES : 0))}
                durationInFrames={shotFrames}
              >
                <Audio src={shot.voiceoverUrl} volume={1.0} />
              </Sequence>
            )}
          </React.Fragment>
        );
      })}

      {enableAnamorphicBars && (
        <>
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "111px",
              backgroundColor: "#000000",
              zIndex: 100,
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              height: "111px",
              backgroundColor: "#000000",
              zIndex: 100,
            }}
          />
        </>
      )}
    </AbsoluteFill>
  );
};
